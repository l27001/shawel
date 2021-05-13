from gtts import gTTS
from random import randint
import os
import subprocess

def mk_voice(text):
	tts = gTTS(text, lang='ru')
	random = randint(1,24000000)
	dir_path = tmp_dir+"/voice"
	if(os.path.isdir(dir_path) == False):
		os.makedirs(dir_path)
	tts.save(f'{dir_path}/{random}.mp3')
	proc = subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','panic','-i',f'{dir_path}/{random}.mp3','-af', 'asetrate=22100*0.5,aresample=48100,atempo=1.9','-ar','16000','-c:a','libopus','-b:a','16k',f'{dir_path}/{random}.opus'], stdout=open(os.devnull, 'wb'))
	proc.wait()
	os.remove(f'{dir_path}/{random}.mp3')
	return f'{dir_path}/{random}.opus'
