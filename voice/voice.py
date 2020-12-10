from gtts import gTTS
from random import randint
import os
import subprocess
dir_path = os.path.dirname(os.path.realpath(__file__))

def mk_voice(text):
	tts = gTTS(text, lang='ru')
	random = randint(1,24000000)
	if(os.path.isdir(dir_path+"/files") == False):
		os.mkdir(dir_path+"/files")
	tts.save(f'{dir_path}/files/{random}.mp3')
	proc = subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','panic','-i',f'{dir_path}/files/{random}.mp3','-ar','16000','-c:a','libopus','-b:a','16k',f'{dir_path}/files/{random}.opus'], stdout=open(os.devnull, 'wb'))
	proc.wait()
	os.remove(f'{dir_path}/files/{random}.mp3')
	return f'{dir_path}/files/{random}.opus'
