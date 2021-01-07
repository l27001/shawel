#!/usr/bin/python3
###1ea4dbccd64c49d58e4e07e1f5dda5e9 может быть полезен
import requests as req
import subprocess,time,os,datetime,schedule
from methods import Methods
dir_path = os.path.dirname(os.path.realpath(__file__))

def job():
	with open(dir_path+"/holiday-count", "r") as f:
		hcount = f.readline()
	hcount = int(hcount)-1
	response = req.get(f"https://holidays.abstractapi.com/v1/?api_key=fe59d2633e604ceba3973fae09e07f6b&country=RU&year={datetime.datetime.now().year}&month={datetime.datetime.now().month}&day={datetime.datetime.now().day}").json()
	with open(dir_path+"/holiday-count", "w") as f:
		f.write(str(hcount))
	result = []
	i = 1
	for n in response:
		result.append(f"{i}) {n['name']}")
		i+=1
	if(len(result) > 0):
		Methods.send(2000000015, "Сегодня есть праздник(и)!\n"+"\n".join(result)+f"\n\nКлюч будет действителен ещё {hcount} раз.")
	elif(hcount <= 15):
		Methods.send(2000000015, f"Ключ HOLIDAY API будет действителен ещё {hcount} раз.")

schedule.every().day.at("10:10").do(job)

try:
	while True:
		schedule.run_pending()
		time.sleep(10)
except KeyboardInterrupt:
	exit()
