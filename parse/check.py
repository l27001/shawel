#!/usr/bin/python3
from PIL import Image
import os, sys
dir_ = sys.argv[1]
tmp_dir = sys.argv[2]
dir_path = os.path.dirname(os.path.realpath(__file__))
files = []
def check():
	for name in sorted(os.listdir(f'{tmp_dir}/parse/{dir_}')):
		im = Image.open(f'{tmp_dir}/parse/{dir_}/{name}')
		white = 0
		for n in im.getdata():
			if(n == (255,255,255)):
				white += 1
		percent = white/(im.size[0]*im.size[1])
		if(percent >= 0.99):
			os.remove(f'{tmp_dir}/parse/{dir_}/{name}')

if(__name__ == '__main__'):
	check()
