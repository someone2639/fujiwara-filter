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

@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')
	for server in client.guilds:
		for channel in server.channels:
			if channel.name == 'general':
				await channel.send("IM\n\nSTUPID")
@client.event
async def on_message(message):
	global filequeue
	channel = message.channel
	iscommand = 0
	if message.content == '!stop':
		print("logging out")
		await channel.send("seeya idiot")
		iscommand = 1
		purgeCache()
		await client.logout()
		return
	elif message.content == '!restart':
		iscommand = 1
		purgeCache()
		print("logging out...")
		await channel.send("restarting...")
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
	if message.author == client.user:
		return
	att = message.attachments
	if len(att) > 0 and isImage(att[0].filename) and iscommand==0:
		myChannel = message.channel
		os.system('wget -P cacheDownload/ '+att[0].url)
		print('new image added:',att[0].filename)
		filequeue.append(att[0].filename)
		# compareImage('cacheDownload/'+att[0].filename)
		numFaces = findFaceMaybe('cacheDownload/'+att[0].filename)
		for file in os.listdir('detectedFaces/'):
			print(file)
			with open('detectedFaces/'+file, 'rb') as f:
				print(os.path.isfile('detectedFaces'+file))
				img = cv.imread('detectedFaces/'+file,0)
				hist = cv.calcHist([img],[0],None,[256],[0,256])
				plt.hist(img.ravel(),256,[0,256])
				plt.show()
				picture = discord.File('detectedFaces/'+file)
				print(channel)
				print(picture)
				await channel.send("face".format(numFaces), file=picture)
		purgeCache()
	else:
		return

client.run(token)