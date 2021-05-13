#!/usr/bin/python3
from bs4 import BeautifulSoup
import requests as req
import subprocess,time,os,datetime,schedule,shutil
from methods import Methods
dir_path = os.path.dirname(os.path.realpath(__file__))

headers = {
    'User-Agent': 'ShawelBot/Parser'
}
def job():
    Methods.log("ZvonkiParser", "Парсер выполняет проверку...")
    resp = req.get("https://engschool9.ru/content/raspisanie.html", headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    src = soup.findAll("iframe")[-1]['src']
    if(os.path.isdir(dir_path+"/parse/zvonki") == False):
        os.mkdir(dir_path+"/parse/zvonki")
    date = datetime.datetime.today().strftime("%H:%M:%S %d.%m.%Y")
    try:
        with open(dir_path+'/parse/result-zvonki.txt','r') as f:
            res = f.readline()
    except FileNotFoundError:
        res = ''
    if(res != src):
        with open(dir_path+'/parse/result-zvonki.txt','w') as f:
            f.write(src)
        for n in os.listdir(dir_path+"/parse/files"):
            os.remove(dir_path+"/parse/files/"+n)
        # p = subprocess.Popen(["wget",f"'{src}'","-qO",dir_path+"/parse/zvonki.pdf",f"--user-agent='{headers['User-Agent']}'"])
        # p.wait()
        with req.get(src, stream=True, headers=headers) as r:
            with open(dir_path+"/parse/zvonki.pdf", "wb") as f:
                shutil.copyfileobj(r.raw, f)
        p = subprocess.Popen(["pdftoppm",dir_path+"/parse/zvonki.pdf",dir_path+"/parse/zvonki/out","-png","-thinlinemode","shape"])
        p.wait()
        p = subprocess.Popen(["python3",f"{dir_path}/parse/check.py","zvonki"])
        p.wait()
        p = subprocess.Popen(["python3",f"{dir_path}/parse/wm.py","zvonki"])
        p.wait()
        attach = []
        mysql_query("DELETE FROM imgs WHERE mark='zvonki'")
        for n in sorted(os.listdir(dir_path+"/parse/zvonki")):
            attach.append(Methods.upload_img('331465308',dir_path+'/parse/zvonki/'+n))
            with open(dir_path+'/parse/zvonki/'+n, 'rb') as f:
                blob = f.read()
            mysql_query("INSERT INTO imgs (`image`,`type`,`size`,`mark`) VALUES (%s, %s, %s, %s)", (blob, n.split('.')[-1], os.path.getsize(dir_path+'/parse/zvonki/'+n), 'zvonki'))
        at = ''
        i = 0
        for n in attach:
            if(i < 1):
                at = n
            else:
                at = at+","+n
            i+=1
        txt = 'Новое расписание звонков\nОбнаружено в '+date
        rasp = Methods.mysql_query("SELECT COUNT(id) FROM `chats` WHERE raspisanie='1'")
        i = 0
        while i < rasp['COUNT(id)']:
            a = []
            r = Methods.mysql_query("SELECT id FROM `chats` WHERE raspisanie='1' LIMIT "+str(i)+", 50", fetch="all")
            for n in r:
                a.append(str(n['id']))
            a = ",".join(a)
            Methods.mass_send(peer_ids=a,message=txt,attachment=at)
            i+=50
            time.sleep(1)
        rasp = Methods.mysql_query("SELECT vkid,raspisanie FROM users WHERE raspisanie>='1'", fetch="all")
        Methods.mysql_query("UPDATE vk SET zvonki='"+at+"'")
        i = 0
        for n in rasp:
            Methods.send(n['vkid'],message=txt,attachment=at,keyboard=Methods.construct_keyboard(b2=Methods.make_button(type="intent_unsubscribe",peer_id=n['vkid'],intent="non_promo_newsletter",label="Отписаться"),inline="true"),intent="non_promo_newsletter")
            i+=1
            time.sleep(1)
        # Methods.send(331465308,message=txt,attachment=at,keyboard=Methods.construct_keyboard(b2=Methods.make_button(type="intent_unsubscribe",peer_id=331465308,intent="non_promo_newsletter",label="Отписаться"),inline="true"),intent="non_promo_newsletter")
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
 
