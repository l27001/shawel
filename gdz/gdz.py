#!/usr/bin/python3
from bs4 import BeautifulSoup
import requests as req
import subprocess,time,os,vk,json,random,pymysql.cursors,datetime
dir_path = os.path.dirname(os.path.realpath(__file__))

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 OPR/70.0.3728.133'
}

def gdz(name,nom):

	ych = {
		'английский':f"https://gdz.ru/class-10/english/reshebnik-spotlight-10-afanaseva-o-v/{nom}-s",
		'геометрия':f"https://gdz.ru/class-10/geometria/atanasyan-10-11/10-class-{nom}/",
		'алгебра':f"https://gdz.ru/class-10/algebra/kolyagin-fedorova/{nom}-nom/",
	}

	try:
		name = ych[name.lower()]
	except KeyError:
		return 2
	resp = req.get(name, headers=headers)
	soup = BeautifulSoup(resp.text, 'html.parser')
	#src = soup.select("div:task-img-container")
#	try:
	result = soup.find_all("div", { "class" : "with-overtask" })
#	print(result[0])
	a = []
	for n in result:
		a.append("https:"+n.select('img')[0]['src'])
	if(os.path.isdir(dir_path+"/files") == False):
		os.mkdir(dir_path+"/files")
#	b = []
#	for n in a:
#		b.append(str(n['src']))
#	except:
#		return 1
	#print(result)
#	for n in result:
#		a.append("https:"+n['src'])
	return a
