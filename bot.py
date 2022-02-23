# bot.py
import os
import discord
import subprocess
import cv2 as cv
import numpy as np
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageFilter
from colorsys import rgb_to_hsv
import src.new_model as new_model
from src.rgb2emoji_single import rgb2singleemoji
# from src import *
# import src.old_model

from discord.ext import commands
from discord.utils import get

import fujiwara_styleGAN.datagen as datagen
import fujiwara_styleGAN.stylegan as stylegan

filequeue = []

valid_img_urls = ['.jpg','.png','.jpeg','.bmp','.tif','.tiff']

def getBannedImgs():
	return [i for i in os.listdir('bannedImages') if i[-3:] != 'ier']


def makeImage(name):
	os.system('touch '+name)
	return name

faceCascade = cv.CascadeClassifier("lbpcascade_animeface/lbpcascade_animeface.xml")
def findFaceMaybe(imagePath):
	print(imagePath)
	im = Image.open(imagePath)
	im = im.convert("RGB")
	im.save(imagePath)
	im.close()
	image = cv.imread(imagePath,-1)
	gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

	ii = Image.open(imagePath)
	x, _ = ii.size
	ii.close()

	faces = faceCascade.detectMultiScale(gray,
									 # detector options
									 scaleFactor = 1.001,
									 minNeighbors = 3,
									 minSize = (int(x / 4), int(x / 4)),
									 # maxSize = (200, 200)
									 ) # TODO: change maxSize to a fraction of image size


	print("[INFO] Found {0} Faces!".format(len(faces)))

	yy = 0
	for (x, y, w, h) in faces:
		# cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
		roi_color = image[y:y + h, x:x + w] 
		print("[INFO] Object found. Saving locally.") 
		fp2 = 'detectedFaces/'+str(hash(imagePath+str(yy))) + '_faces.jpg'
		cv.imwrite(fp2, roi_color)
		im = Image.open(fp2)
		im = im.resize((128, 128))
		im.save('detectedFaces2/'+str(hash(imagePath+str(yy))) + '_faces.jpg')
		im.close()
		yy+= 1

	status = cv.imwrite(makeImage('faces_detected.jpg'), image)
	print("[INFO] Image faces_detected.jpg written to filesystem: ", status)
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
		if i in fname.lower():
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

		# plt.show(

def color2name(rgbt):
	r = rgbt[0]
	g = rgbt[1]
	b = rgbt[2]
	d = rgb_to_hsv(r, g, b)
	h = d[0]
	s = d[1]
	v = d[2]

	if v < 50:
		return "black"
	if s < 10:
		return "white"

	if 0 <= h <= 20 or 345 <= h <= 360:
		return "red"
	if 21 <= h <= 47:
		return "orange"
	if 48 <= h <= 69:
		return "yellow"
	if 70 <= h <= 150:
		return "green"
	if 151 <= h <= 271:
		return "blue"
	if 272 <= h <= 344:
		return "purple"



# stackoverflow (modded by arthur) (further modded by me)
def closest_colour(requested_colour): # requested_color is a 3-tuple
	min_dist = 9999999
	min_colour = None
	for key in rgb2singleemoji:
		r_c, g_c, b_c = ImageColor.getrgb("#"+key.upper())
		rd = (r_c - requested_colour[0]) ** 2
		gd = (g_c - requested_colour[1]) ** 2
		bd = (b_c - requested_colour[2]) ** 2
		if (rd + gd + bd) < min_dist:
		  min_dist = rd + gd + bd
		  min_colour = rgb2singleemoji[key]
	return min_colour
# end stackoverflow

def color_emoji(requested_colour):
	closest_name = closest_colour(requested_colour)
	# print(closest_name)
	return closest_name

emojifont = ImageFont.truetype("TwitterColorEmoji-SVGinOT.ttf", 16)
def m2img(txt):
	wd0 = len(txt.split("\n"))

	wd = (16 * wd0) - 14
	image = Image.new("RGBA", (wd, wd), color=(54, 57, 53, 255))
	draw = ImageDraw.Draw(image)

	a = txt.split("\n")

	x = 1
	y = 1
	for i in a:
		for j in i:
			ii = Image.open(os.path.expanduser("~/Devel/twemoji/assets/72x72/%x.png" % ord(j)))
			ii2 = ii.resize((16, 16))
			image.paste(ii2, (x, y))
			# draw.text((x, y), j, font=emojifont)
			x += 16
			ii.close()
			ii2.close()
		y += 16
		x = 1

	image.save("emoji_img_generated_by_fujiwara_filter.png")
	return "emoji_img_generated_by_fujiwara_filter.png"


def emojify(filepath, imsize):
	im = Image.open(filepath)
	im = im.resize([imsize, imsize], resample = Image.LANCZOS)
	im = im.convert("RGB")

	mes = ""

	for i in range(imsize):
		for j in range(imsize):
			glyph = color_emoji(im.getpixel((j,i)))
			mes += glyph
		mes += "\n"

	print(mes)
	return mes

load_dotenv()
token = os.getenv('DISCORD_TOKEN')


client = discord.Client()

myChannel = None


bot = commands.Bot(command_prefix='!')

# @bot.command(pass_context=True)
# @commands.has_role("Admin") # This must be exactly the name of the appropriate role
# async def addrole(ctx):
#     member = ctx.message.author
#     role = get(member.server.roles, name="Test")
#     await bot.add_roles(member, role)


async def channelSend(channel, mesg,f=None):
	try:
		if f:
			await channel.send(mesg, file=f)
		else:
			await channel.send(mesg)
	except Exception as e:
		pass

@client.event
async def on_ready():
	print(f'{client.user} has connected to Discord!')
	for server in client.guilds:
		for channel in server.channels:
			if channel.name == 'overlord-bot-commands':
				await channelSend(channel, "IM\n\nSTUPID")

def reddit(message):
	print("reddit")


tempCreatedPaths = []

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
		elif message.content == "i agree":
			x = [i for i in message.author.guild.roles if i.name == "fnf64"][0]
			print(x.id)
			await message.author.add_roles(x)
			await message.delete()
		else:
			await message.delete()
		return
	iscommand = 0

	if channel.name == "overlord-bot-commands":
		t = message.content.split()
		if "!s" in message.content:
			ch = t[1]
			ms = message.content.split(ch)[1]
			newch = discord.utils.get(client.get_all_channels(), name=ch)

			att = message.attachments
			if len(att) > 0 and isImage(att[0].filename):
				os.system('wget -P cacheDownload/ '+att[0].url)
				picture = discord.File('cacheDownload/'+att[0].filename)
				await newch.send(ms, file=picture)
			else:
				await newch.send(ms)
			
			

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
	elif message.content == 'true' and channel.name == "normal-people-bot-commands":
		iscommand = 1
		await channel.send("i can see it")
	elif "!emojify" in message.content:
		t = message.content.split()
		wd = int(t[1])
		iscommand = 1

		if wd > 64:
			f = discord.File("yourstupid.png")
			await channel.send("imagine trying to run that on my poor circuits 😂 pick a smaller size (limit 64)", file=f)
		else:
			att = message.attachments
			url = ""
			fname =""
			if len(att) == 0:
				if len(t) == 3:
					url = t[2]
					if url[0] == "<":
						url = url[1:-1]
					fname = str(hash(t[2]))+url[-4:]
			else:
				url = att[0].url
				fname = att[0].filename

			to_image = False

			if len(t) == 3 and t[2] == "image":
				to_image = True

			print(url, fname)

			if isImage(url):
				os.system('wget -P cacheDownload/ '+url)
				nn = url.split("/")[-1]
				ms = emojify('cacheDownload/'+nn, wd)
				if to_image:
					pa = m2img(ms)
					f = discord.File(pa)
					await channel.send("", file=f)
				else:
					await channel.send(ms)
	if message.content == '!printqueue':
		iscommand = 1
		print(filequeue)
	if message.content == '!listBannedImgs':
		iscommand = 1
		print(getBannedImgs())
	if message.content == '!purge':
		iscommand = 1
		purgeCache()
	if message.content == "!fujiwara":
		os.system("python3 fujiwara_styleGAN/stylegan.py %s/monstrosity.png" % os.pwd())
		fil = discord.File("monstrosity.png")
		await channel.send("filter!", file=fil)
		iscommand = 1

	
	att = message.attachments
	if len(att) > 0 and isImage(att[0].filename) and iscommand==0:
		myChannel = message.channel
		os.system('wget -P cacheDownload/ '+att[0].url)
		print('new image added:',att[0].filename)
		filequeue.append(att[0].filename)
		# compareImage('cacheDownload/'+att[0].filename)
		if new_model.isFujiwara('cacheDownload/'+att[0].filename):
			matches = 0
			numFaces = findFaceMaybe('cacheDownload/'+att[0].filename)
			picture = discord.File('cacheDownload/'+att[0].filename)
			for file in os.listdir('detectedFaces/'):
				picture = discord.File('detectedFaces/'+file)

			await channel.send("FUJIWARA DETECTED", file=picture)

		# if isFujiwara:
		# 	await channel.send("FUJIWARA DETECTED", file=picture)
		# if matches < 10 and matches > 0:
		# 	if channel.name == "normal-people-bot-commands":
		# 		await channel.send("%d faces detected" % numFaces, file=discord.File("./faces_detected.jpg"))
		# elif matches == 0:
		# 	pass
		# else:
		# 	await channel.send("FUJIWARA DETECTED", file=picture)
		purgeCache()
	else:
		return


client.run(token)