#!/usr/bin/python3
from bs4 import BeautifulSoup
import requests as req
import subprocess,time,os,datetime,schedule,shutil
from methods import Methods
from config import tmp_dir
dir_path = os.path.dirname(os.path.realpath(__file__))

headers = {
    'User-Agent': 'ShawelBot/Parser'
}
def job(mode=0):
    Methods.log("ZvonkiParser", "Парсер выполняет проверку...")
    resp = req.get("https://engschool9.ru/content/raspisanie.html", headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    src = soup.findAll("iframe")[-1]['src']
    if(os.path.isdir(tmp_dir+"/parse/zvonki") == False):
        os.makedirs(tmp_dir+"/parse/zvonki")
    date = datetime.datetime.today().strftime("%H:%M:%S %d.%m.%Y")
    if(mode == 0):
        try:
            with open(dir_path+'/parse/result-zvonki.txt','r') as f:
                res = f.readline()
        except FileNotFoundError:
            res = None
    else:
        res = None
    if(res != src):
        with req.get(src, stream=True, headers=headers) as r:
            with open(tmp_dir+"/parse/zvonki.pdf", "wb") as f:
                shutil.copyfileobj(r.raw, f)
        p = subprocess.Popen(["pdftoppm",tmp_dir+"/parse/zvonki.pdf",tmp_dir+"/parse/zvonki/out","-png","-thinlinemode","shape"])
        p.wait()
        p = subprocess.Popen(["python3",f"{dir_path}/parse/check.py","zvonki",tmp_dir])
        p.wait()
        p = subprocess.Popen(["python3",f"{dir_path}/parse/wm.py","zvonki",tmp_dir])
        p.wait()
        attach = []
        Methods.mysql_query("DELETE FROM imgs WHERE mark='zvonki'")
        for n in sorted(os.listdir(tmp_dir+"/parse/zvonki")):
            attach.append(Methods.upload_img('331465308',tmp_dir+'/parse/zvonki/'+n))
            with open(tmp_dir+'/parse/zvonki/'+n, 'rb') as f:
                blob = f.read()
            Methods.mysql_query("INSERT INTO imgs (`image`,`type`,`size`,`mark`) VALUES (%s, %s, %s, %s)", (blob, n.split('.')[-1], os.path.getsize(tmp_dir+'/parse/zvonki/'+n), 'zvonki'))
        txt = 'Новое расписание звонков\nОбнаружено в '+date+'\nДля отписки используйте команду \'/рассылка\''
        if(mode == 0):
            rasp = Methods.mysql_query("SELECT COUNT(id) FROM `chats` WHERE raspisanie='1'")
            i = 0
            while i < rasp['COUNT(id)']:
                a = []
                r = Methods.mysql_query("SELECT id FROM `chats` WHERE raspisanie='1' LIMIT "+str(i)+", 50", fetch="all")
                for n in r:
                    a.append(str(n['id']))
                a = ",".join(a)
                Methods.mass_send(peer_ids=a,message=txt,attachment=attach)
                i+=50
                time.sleep(1)
            rasp = Methods.mysql_query("SELECT vkid,raspisanie FROM users WHERE raspisanie>='1'", fetch="all")
            i = 0
            for n in rasp:
                Methods.send(n['vkid'],message=txt,attachment=attach,keyboard=Methods.construct_keyboard(b2=Methods.make_button(type="intent_unsubscribe",peer_id=n['vkid'],intent="non_promo_newsletter",label="Отписаться"),inline="true"),intent="non_promo_newsletter")
                i+=1
                time.sleep(.5)
        else:
            Methods.send(331465308,message=txt,attachment=attach)
        Methods.mysql_query("UPDATE vk SET zvonki='"+','.join(at)+"'")
        with open(dir_path+'/parse/result-zvonki.txt','w') as f:
            f.write(src)
        for n in os.listdir(tmp_dir+"/parse/zvonki"):
            os.remove(tmp_dir+"/parse/zvonki/"+n)
        Methods.log("ZvonkiParser", "Обнаружено новое расписание звонков.")
        time.sleep(60)
    else:
        Methods.log("ZvonkiParser", "Новое расписание звонков не было обнаружено.")

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
            Methods.log("ZvonkiParser-ERROR", f"Произошла ошибка.\n\n{e}")
            Methods.send(331465308, f"С парсером звонков что-то не так!\n\n{e}")
            time.sleep(60)

if(__name__ == '__main__'):
    run()
 
