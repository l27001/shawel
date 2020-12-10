#!/usr/bin/python3
from PIL import Image
import os

files = []
for n in sorted(os.listdir('yes')):
	im = Image.open(f'yes/{n}')
	white = 0
	for n in im.getdata():
		if(n == (255,255,255)):
			white += 1
	print(im.size[0]*im.size[1])
	print(white)
	percent = white/(im.size[0]*im.size[1])
	print(percent)
	if(percent < 0.99):
		print('Correct')
	else:
		print('Must be deleted')
	print()
