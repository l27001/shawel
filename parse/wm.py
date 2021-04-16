#!/usr/bin/python3
from PIL import Image
import os, sys
dir_ = sys.argv[1]
dir_path = os.path.dirname(os.path.realpath(__file__))

for n in sorted(os.listdir(f"{dir_path}/{dir_}")):
	im = Image.open(f"{dir_path}/{dir_}/{n}")
	onew = 0
	oneh = 0
	twow = 0
	twoh = 0
	w,h = (0,0)
	W,H = im.size

	while h < H:
		while w < W:
			pixel = im.getpixel((w,h))
			if(pixel != (255,255,255)):
				if(w < onew or onew == 0):
					onew = w
				if(oneh == 0):
					oneh = h

			if(pixel != (255,255,255)):
				if(w > twow):
					twow = w
				twoh = h
			w+=1
		h+=1
		w = 0

	im = im.crop((onew,oneh-5,twow,twoh+5))
	img = Image.open(f"{dir_path}/../demotivator/200.png")
	img = img.convert("RGBA")
	im = im.convert("RGBA")
	W,H = im.size
	w,h = img.size
	im.paste(img, (W//2-w//2,H//2-h//2), img)
	im = im.convert("RGB")
	im.save(f'{dir_path}/{dir_}/{n}')
