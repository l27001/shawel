#!/usr/bin/python3
from methods import Methods
from time import sleep,time
import schedule
from random import randint as random

def job():
	vk = Methods.bd_exec("SELECT vlaga,autopoliv FROM vk")
	rand = random(7,15)
	if((vk['vlaga'] - rand) < 0):
		rand = vk['vlaga']
	if(vk['autopoliv'] < int(time()) and vk['vlaga'] > 0):
		Methods.bd_exec(f"UPDATE vk SET `vlaga`=`vlaga`-{rand}")
		if((vk['vlaga']-rand) == 0 and vk['vlaga'] > 0):
			Methods.send(peer_id=2000000015,
#				message="Щавель высох.",
#				attachment="photo-183256712_457239040")
				attachment="photo331465308_457246524")
			sleep(60)

schedule.every().hour.at(":00").do(job)

def run():
	try:
		while True:
			schedule.run_pending()
			sleep(1)
	except KeyboardInterrupt:
		exit()

if(__name__ == '__main__'):
	run()
