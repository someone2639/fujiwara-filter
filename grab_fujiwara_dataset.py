import os
import discord
import subprocess
import cv2 as cv
import numpy as np
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageFilter
from colorsys import rgb_to_hsv
# importing google_images_download module

def makeImage(name):
	os.system('touch '+name)
	return name

valid_img_urls = ['.jpg','.png','.jpeg','.bmp','.tif','.tiff']

def isImage(fname):
	global valid_img_urls
	for i in valid_img_urls:
		if i in fname.lower():
			return True
	return False

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
		fp2 = 'detectedFaces2/'+str(hash(imagePath+str(yy))) + '_faces.jpg'
		cv.imwrite(fp2, roi_color)
		im = Image.open(fp2)
		im = im.resize((128, 128))
		im.save(fp2)
		im.close()
		yy+= 1

	status = cv.imwrite(makeImage('faces_detected.jpg'), image)
	print("[INFO] Image faces_detected.jpg written to filesystem: ", status)
	return len(faces)

# from bing_image_downloader import downloader
# downloader.download("Chika Fujiwara", limit=1000,  output_dir='dataset', 
# adult_filter_off=True, force_replace=False, timeout=60)


import sys, os

fl = os.listdir(sys.argv[1])

for i in fl:
	im = Image.open(sys.argv[1] + i)
	x, y = im.size
	im.close()
	if x != 128 or y != 128:
		print("FUCK %s" % i)

