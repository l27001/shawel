#!/usr/bin/python3
import requests, time, multiprocessing, argparse, subprocess
from OpenSSL.SSL import Error as VeryError
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError

parser = argparse.ArgumentParser()
parser.add_argument('-d','--debug', action='store_true', help="enable debug mode")
args = parser.parse_args()
import config
import builtins
builtins.DEBUG = args.debug

from config import groupid
from other import dir_path, api, BL
from commands import Commands
from methods import Methods

###
def start():
	try:
		scrname = api.groups.getById(group_id=groupid)[0]
		builtins.scrname = scrname['screen_name']
		lp = api.groups.getLongPollServer(group_id=groupid)
		server = lp['server']
		key = lp['key']
		try:
			with open(dir_path+"/TS", 'r') as f:
				ts = f.read()
		except FileNotFoundError:
			ts = lp['ts']
		unp = subprocess.Popen(["python3",dir_path+"/unpoliv.py"])
		parse = subprocess.Popen(["python3",dir_path+"/parse.py"])
		Methods.log("INFO",f"{scrname['name']} успешно запущен.")
		while True:
			try:
				response = requests.get(server+"?act=a_check&key="+key+"&ts="+ts+"&wait=20",timeout=22).json()
				if 'failed' in response:
					lp = api.groups.getLongPollServer(group_id=groupid)
					server = lp['server']
					key = lp['key']
					if(DEBUG == True):
						Methods.log("Debug","Получен некорректный ответ. Ключ обновлен.")
					continue
				if(response['ts'] != ts):
					ts = response['ts']
					with open(dir_path+"/TS", 'w') as f:
						f.write(ts)
					for res in response['updates']:
						if(BL.count(res['object']['message']['from_id']) == 0):
							t = multiprocessing.Process(target=Commands, args=(res,))
							t.start()
							#Commands(res) #Обработка команды
			except(VeryError, ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
				Methods.log("WARN","Сервер не ответил. Жду 3 секунды перед повтором.")
				time.sleep(3)
	except KeyboardInterrupt:
		Methods.log("INFO","Завершение...")
		unp.terminate()
		parse.terminate()
		exit()
	except(ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
		Methods.log("ERROR","Запуск не удался. Повтор через 10 секунд.")
		time.sleep(10)
		start()
Methods.log("INFO",f"Запуск бота...")
start()