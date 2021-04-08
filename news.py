#!/usr/bin/python3
from bs4 import BeautifulSoup
import requests as req
import subprocess,time,os,datetime,schedule
from methods import Methods
dir_path = os.path.dirname(os.path.realpath(__file__))
anotify = None

Word = ['возобновляются', 'возобновятся', 'отменяются',
    'приостанавливаются', 'приостанавливается', 'приостановлен',
    'занятия', 'традиционному', 'обучения', 'возвращаются',
    'дистанционное', 'традиционное', 'обучение', 'дистанционного',
    'дистанционном', 'карантин']
headers = {
    'User-Agent': 'ShawelBot/Parser'
}

def job():
    if(os.path.isdir(dir_path+"/news/files") == False):
        os.mkdir(dir_path+"/news/files")
    resp = req.get("https://engschool9.ru", headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    obj = soup.find("div", class_="oneNews")
    date = obj.find("div", class_="newsDate")
    date = date.text
    obj = obj.find("div", class_="newsContent")
    img = obj.find("img")
    text = obj.find("p")
    if(text == None):
        text = obj.find("h2")
    if(text == None):
        text = obj.find("strong")
    text = text.text
    try:
        with open(dir_path+'/news/result.txt','r') as f:
            res = f.readline()
    except FileNotFoundError:
        res = ''
    Ans = text.split(" ")
    new = []
    for k in Ans:
        new.append(k.lower)
    if(date != res and len(list(set(new) & set(Word))) > 0):
        with open(dir_path+'/news/result.txt','w') as f:
           f.write(date)
        if(img != None):
            r = "."+img['src'].split(".")[-1]
            Methods.download_img(img['src'], dir_path+"/news/files/img"+r)
            attach = Methods.upload_img(331465308, dir_path+"/news/files/img"+r)
            os.remove(dir_path+"/news/files/img"+r)
        else:
            attach = ''
        link = obj.find("a", class_="oneNewsMore")
        Methods.mass_send([331465308, 2000000016], text+"\n\nhttps://engschool9.ru"+link['href'], attachment=attach)
        anotify = None

schedule.every().hour.at(":00").do(job)
schedule.every().hour.at(":30").do(job)

def run():
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            if(anotify != e):
                anotify = e
                Methods.log("Parser2-ERROR", f"Произошла ошибка.\n\n{e}")
                Methods.send(331465308, f"С парсером #2 что-то не так!\n\n{e}")
            time.sleep(60)

if(__name__ == '__main__'):
    run()
