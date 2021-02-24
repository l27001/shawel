#!/usr/bin/python3
from bs4 import BeautifulSoup
import requests as req
import subprocess,time,os,datetime,schedule
from methods import Methods
dir_path = os.path.dirname(os.path.realpath(__file__))

headers = {
    'User-Agent': 'ShawelBot/Parser'
}
def job():
    #resp = req.get("https://engschool9.ru/content/raspisanie.html", headers=headers, proxies={"http":proxy,"https":proxy})
    Methods.log("Parser", "Парсер выполняет проверку...")
    resp = req.get("https://engschool9.ru/content/raspisanie.html", headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    src = soup.find("iframe")['src']
    if(os.path.isdir(dir_path+"/parse/files") == False):
        os.mkdir(dir_path+"/parse/files")
    date = datetime.datetime.today().strftime("%H:%M:%S %d.%m.%Y")
    Methods.bd_exec(f"UPDATE vk SET `rasp-checked`='{date}'")
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
        #p = subprocess.Popen(["wget",src,"-qO",dir_path+"/parse/raspisanie.pdf","--user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 OPR/70.0.3728.133'", "-e", "use_proxy=yes", "-e", f"https_proxy={proxy}", "-e", f"http_proxy={proxy}"])
        p = subprocess.Popen(["wget",src,"-qO",dir_path+"/parse/raspisanie.pdf",f"--user-agent='{headers['User-Agent']}'"])
        p.wait()
        p = subprocess.Popen(["pdftoppm",dir_path+"/parse/raspisanie.pdf",dir_path+"/parse/files/out","-png"])
        p.wait()
        p = subprocess.Popen(["python3",f"{dir_path}/parse/check.py"])
        p.wait()
        p = subprocess.Popen(["python3",f"{dir_path}/parse/wm.py"])
        p.wait()
        attach = []
        for n in sorted(os.listdir(dir_path+"/parse/files")):
            attach.append(Methods.upload_img('331465308',dir_path+'/parse/files/'+n))
            at = ''
            i = 0
        for n in attach:
            if(i < 1):
                at = n
            else:
                at = at+","+n
            i+=1
        txt = 'Новое расписание\nОбнаружено в '+date
        rasp = Methods.bd_exec("SELECT COUNT(id) FROM `chats` WHERE raspisanie='1'")
        i = 0
        while i < rasp['COUNT(id)']:
            a = []
            r = Methods.bd_exec("SELECT id FROM `chats` WHERE raspisanie='1' LIMIT "+str(i)+", 50", fetch="all")
            for n in r:
                a.append(str(n['id']))
            a = ",".join(a)
            Methods.mass_send(peer_ids=a,message=txt,attachment=at)
            i+=50
            time.sleep(1)
        rasp = Methods.bd_exec("SELECT vkid,raspisanie FROM users WHERE raspisanie>='1'", fetch="all")
        Methods.bd_exec("UPDATE vk SET rasp='"+at+"'")
        i = 0
        #while i < len(rasp):
            #a = []
            #r = Methods.bd_exec("SELECT vkid FROM users WHERE raspisanie>='1'", fetch="all")
        for n in rasp:
            Methods.send(n['vkid'],message=txt,attachment=at,keyboard=Methods.construct_keyboard(b2=Methods.make_button(type="intent_unsubscribe",peer_id=n['vkid'],intent="non_promo_newsletter",label="Отписаться"),inline="true"),intent="non_promo_newsletter")
            i+=1
            time.sleep(1)
        subprocess.Popen("rm /srv/http/shawel/rasp-files/*", shell=True)
        subprocess.Popen(f"cp {dir_path}/parse/files/* /srv/http/shawel/rasp-files/", shell=True)
        Methods.bd_exec(f"UPDATE vk SET `rasp-updated`='{date}'")
        Methods.log("Parser", "Обнаружено новое расписание.")
        time.sleep(60)
    else:
        Methods.log("Parser", "Новое расписание не было обнаружено.")

schedule.every().hour.at(":00").do(job)
schedule.every().hour.at(":30").do(job)

def run():
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        Methods.log("Parser-ERROR", f"Произошла ошибка.\n\n{e}")
        Methods.send(331465308, f"С парсером что-то не так!\n\n{e}")

if(__name__ == '__main__'):
    run()
