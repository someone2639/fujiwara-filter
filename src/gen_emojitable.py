import sys, os
from PIL import Image, ImageStat

files = os.listdir(sys.argv[1])

keys = {}

for x in files:
	codepoints = x.split(".")[0].split("-")
	# if len(codepoints) > 1:
	# 	continue
	finalStr = ""
	for i in codepoints:
		finalStr += chr(int(i, 16))
	
	im = Image.open(sys.argv[1] + x)
	im = im.convert("RGBA")
	sorter = im.getcolors()
	commoncolor = sorted(sorter)[::-1][0][1]


	# print(sorted(sorter)[::-1][0][0])
	# s = ImageStat.Stat(im)

	t = commoncolor
	
	rgb = "%02X%02X%02X" % (t[0], t[1], t[2])

	if rgb not in keys:
		keys[rgb] = "mario"
		print("    \"%s\" : \"%s\"," % (rgb, finalStr))

