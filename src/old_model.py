
import os
import cv2 as cv
import discord

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


def isFujiwara(file):
	print(file)
	tM = 0
	foundFujiwara = False
	with open('detectedFaces/'+file, 'rb') as f:
		print(os.path.isfile('detectedFaces'+file))
		img = cv.imread('detectedFaces/'+file,-1)
		hsv = cv.cvtColor(img,cv.COLOR_BGR2HSV)

		hist = cv.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
		print(hist[0])
		print(len(hist))
		if checkColors(hist) > tM:
			tM = checkColors(hist)
		# plt.imshow(hist,interpolation = 'nearest')
		# plt.show()

		# plt.hist(img.ravel(),256,[0,256])
		# plt.show()
		picture = discord.File('detectedFaces/'+file)
		# print(channel)
		print(picture)

	return tM > 10

