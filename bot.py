# bot.py
import os
import discord
import subprocess
import cv2 as cv
import numpy as np
from dotenv import load_dotenv
from matplotlib import pyplot as plt

filequeue = []

valid_img_urls = ['.jpg','.png','.jpeg','.bmp','.tif','.tiff']

def getBannedImgs():
	return [i for i in os.listdir('bannedImages') if i[-3:] != 'ier']

def checkColors(hist):
	validH = [0,  20 ]
	validS = [75, 100]
	matchCount = 0
	for i in range(validH[0],validH[1]):
		S = hist[i]
		for val in S:
			if val > validS[0] and val < validS[1]:
				matchCount+=1
	print(matchCount)
	return matchCount


def makeImage(name):
	os.system('touch '+name)
	return name

def findFaceMaybe(imagePath):
	print(imagePath)
	image = cv.imread(imagePath,-1)
	gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

	faceCascade = cv.CascadeClassifier("lbpcascade_animeface/lbpcascade_animeface.xml")
	faces = faceCascade.detectMultiScale(gray,
                                     # detector options
                                     scaleFactor = 1.001,
                                     minNeighbors = 3,
                                     minSize = (40, 40),
                                     # maxSize = (200, 200)
                                     ) # TODO: change maxSize to a fraction of image size


	print("[INFO] Found {0} Faces!".format(len(faces)))

	for (x, y, w, h) in faces:
		cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
		roi_color = image[y:y + h, x:x + w] 
		print("[INFO] Object found. Saving locally.") 
		cv.imwrite('detectedFaces/'+str(w) + str(h) + '_faces.jpg', roi_color) 

	# status = cv.imwrite(makeImage('faces_detected.jpg'), image)
	# print("[INFO] Image faces_detected.jpg written to filesystem: ", status)
	return len(faces)


def purgeCache():
	global filequeue
	filequeue = []
	# you had better not change this line or else i'll take a bullet
	# train to your house and toss your salad
	os.system('rm -rf cacheDownload detectedFaces && mkdir cacheDownload detectedFaces')

def isImage(fname):
	global valid_img_urls
	for i in valid_img_urls:
		if i in fname:
			return True
	return False

def compareImage(file1):
	img = cv.imread(file1,0)
	for file in getBannedImgs():
		template = cv.imread('bannedImages/'+file,0)
		w, h = template.shape[::-1] 
		method = cv.TM_CCOEFF
		res = cv.matchTemplate(img, template, method)
		print(res)
		min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
		print(min_val, max_val, min_loc, max_loc)
		top_left = max_loc
		bottom_right = (top_left[0] + w, top_left[1] + h)

		cv.rectangle(img,top_left, bottom_right, 255, 2)

		plt.subplot(121),plt.imshow(res,cmap = 'gray')
		plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
		plt.subplot(122),plt.imshow(img,cmap = 'gray')
		plt.title('Detected Point'), plt.xticks([]), plt.yticks([])

		# plt.show()


load_dotenv()
token = os.getenv('DISCORD_TOKEN')


client = discord.Client()

myChannel = None

from discord.ext import commands
from discord.utils import get


bot = commands.Bot(command_prefix='!')

# @bot.command(pass_context=True)
# @commands.has_role("Admin") # This must be exactly the name of the appropriate role
# async def addrole(ctx):
#     member = ctx.message.author
#     role = get(member.server.roles, name="Test")
#     await bot.add_roles(member, role)


async def channelSend(channel, mesg):
	try:
		await channel.send(mesg)
	except Exception as e:
		pass

@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')
	for server in client.guilds:
		for channel in server.channels:
			if channel.name == 'general':
				await channelSend(channel, "IM\n\nSTUPID")

def reddit(message):
	print("reddit")

@client.event
async def on_message(message):
	global filequeue
	channel = message.channel
	print(channel.name, message.author)
	if message.author == client.user:
		return
	if channel.name == "rom-hack-portal":
		return
	if channel.name == "reddit":
		reddit(message)
		return

	if channel.name == "terms-and-conditions":
		if message.content == "im stupid":
			x = [i for i in message.author.guild.roles if i.name == "stupid"][0]
			print(x.id)
			await message.author.add_roles(x)
			await message.delete()
		else:
			await message.delete()
		return
	iscommand = 0
	if message.content == '!stop':
		print("logging out")
		await channelSend(channel, "seeya idiot")
		iscommand = 1
		purgeCache()

		await client.logout()
		return
	elif message.content == '!restart':
		iscommand = 1
		purgeCache()
		print("logging out...")
		await channelSend(channel, "restarting...")
		subprocess.call(['sleep 2s && python3 bot.py'],shell = True)
		await client.logout()
		return
	if message.content == '!printqueue':
		iscommand = 1
		print(filequeue)
	if message.content == '!listBannedImgs':
		iscommand = 1
		print(getBannedImgs())
	if message.content == '!purge':
		iscommand = 1
		purgeCache()
	
	att = message.attachments
	if len(att) > 0 and isImage(att[0].filename) and iscommand==0:
		myChannel = message.channel
		os.system('wget -P cacheDownload/ '+att[0].url)
		print('new image added:',att[0].filename)
		filequeue.append(att[0].filename)
		# compareImage('cacheDownload/'+att[0].filename)
		matches = 0
		numFaces = findFaceMaybe('cacheDownload/'+att[0].filename)
		for file in os.listdir('detectedFaces/'):
			print(file)
			with open('detectedFaces/'+file, 'rb') as f:
				print(os.path.isfile('detectedFaces'+file))
				img = cv.imread('detectedFaces/'+file,-1)
				hsv = cv.cvtColor(img,cv.COLOR_BGR2HSV)

				hist = cv.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
				print(hist[0])
				print(len(hist))
				tM = checkColors(hist)
				if tM > matches:
					matches=tM
				# plt.imshow(hist,interpolation = 'nearest')
				# plt.show()

				# plt.hist(img.ravel(),256,[0,256])
				# plt.show()
				picture = discord.File('detectedFaces/'+file)
				print(channel)
				print(picture)
		if matches < 10:
			await channelSend(channel, "%d faces detected" % numFaces)
		else:
			await channelSend(channel, "FUJIWARA DETECTED")
		purgeCache()
	else:
		return

client.run(token)