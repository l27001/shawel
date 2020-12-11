#!/usr/bin/python3
from PIL import Image
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
files = []
def check():
	for name in sorted(os.listdir(dir_path+'/files')):
		im = Image.open(f'{dir_path}/files/{name}')
		white = 0
		for n in im.getdata():
			if(n == (255,255,255)):
				white += 1
		percent = white/(im.size[0]*im.size[1])
		if(percent < 0.99):
			os.remove(f'{dir_path}/files/{name}')

if(__name__ == '__main__'):
	check()
