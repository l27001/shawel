#!/usr/bin/python3
from bs4 import BeautifulSoup
import requests as req
import subprocess,time,os,datetime,schedule
from methods import Methods
dir_path = os.path.dirname(os.path.realpath(__file__))

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 OPR/70.0.3728.133'
}
def job():
	resp = req.get("https://engschool9.ru/content/raspisanie.html", headers=headers)
	soup = BeautifulSoup(resp.text, 'html.parser')
	src = soup.find("iframe")['src']

	if(os.path.isdir(dir_path+"/parse/files") == False):
		os.mkdir(dir_path+"/parse/files")

	try:
		with open(dir_path+'/parse/result.txt','r') as f:
			res = f.readline()
	except FileNotFoundError:
		res = ''
	if(res != src):
		with open(dir_path+'/parse/result.txt','w') as f:
			f.write(src)
		for n in os.listdir(dir_path+"/parse/files"):
			os.remove(dir_path+"/parse/files/"+n)
		p = subprocess.Popen(["wget",src,"-qO",dir_path+"/parse/raspisanie.pdf","--user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 OPR/70.0.3728.133'"])
		p.wait()
		p = subprocess.Popen(["pdftoppm",dir_path+"/parse/raspisanie.pdf",dir_path+"/parse/files/out","-png"])
		p.wait()
		p = subprocess.Popen(["python3",f"{dir_path}/parse/check.py"])
		p.wait()
		attach = []
		for n in sorted(os.listdir(dir_path+"/parse/files")):
			attach.append(Methods.upload_img('574214420',dir_path+'/parse/files/'+n))
			at = ''
			i = 0
		for n in attach:
			if(i < 1):
				at = n
			else:
				at = at+","+n
			i+=1
		rasp = Methods.bd_exec("SELECT vkid FROM users WHERE raspisanie='1'")
		Methods.bd_exec("UPDATE vk SET rasp='"+at+"'")
		i = 0
		txt = 'Новое расписание\nОбнаружено в '+datetime.datetime.today().strftime("%H:%M:%S %d.%m.%Y")
		while i < len(rasp):
			a = []
			r = Methods.bd_exec("SELECT vkid FROM users WHERE raspisanie='1' LIMIT "+str(i)+", 50", fetch="all")
			for n in r:
				a.append(str(n['vkid']))
			a = ",".join(a)
			Methods.mass_send(peer_ids=a,message=txt,attachment=at)
			i+=50
			time.sleep(1)

		rasp = Methods.bd_exec("SELECT id FROM `chat-rasp`", fetch="all")
		i = 0
		while i < len(rasp):
			a = []
			r = Methods.bd_exec("SELECT id FROM `chat-rasp` LIMIT "+str(i)+", 50", fetch="all")
			for n in r:
				a.append(str(n['id']))
			a = ",".join(a)
			Methods.mass_send(peer_ids=a,message=txt,attachment=at)
			i+=50
			time.sleep(1)
		time.sleep(60)

schedule.every().hour.at(":00").do(job)
schedule.every().hour.at(":30").do(job)

def run():
	try:
		while True:
			schedule.run_pending()
			time.sleep(1)
	except KeyboardInterrupt:
		exit()

if(__name__ == '__main__'):
	job()
