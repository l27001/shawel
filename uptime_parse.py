#!/usr/bin/python3
import requests
from time import sleep
from methods import Methods

def job():
    res = requests.post('https://api.uptimerobot.com/v2/getMonitors?format=json', json={"api_key":"ur1048433-f7ea5b960f4eb0177d8cd42f"}).json()
    # print(res)
    monitors = res['monitors']
    # upbd = Methods.bd_exec("SELECT * FROM uptime")
    # print(upbd)
    stat = []
    for k in monitors:
        data = Methods.bd_exec(f"SELECT * FROM uptime WHERE id='{k['id']}'")
        if(data == None):
            Methods.bd_exec(f"INSERT INTO uptime (`id`,`status`) VALUES ('{k['id']}','{k['status']}')")
            if(k['status'] == 9):
                stat.append(f"⚠ {k['friendly_name']} Недоступен!")
        if(data['status'] != k['status']):
            Methods.bd_exec(f"UPDATE uptime SET status='{k['status']}' WHERE id='{k['id']}'")
            if(k['status'] == 9 or k['status'] == 8):
                stat.append(f"⚠ {k['friendly_name']} Недоступен!")
            elif(k['status'] == 0):
                stat.append(f"❓ {k['friendly_name']} Приостановлен")
            elif(k['status'] == 2):
                stat.append(f"✅ {k['friendly_name']} Доступен")
    text = "\n".join(stat)
    if(len(text) > 0):
        Methods.send(331465308, text)

while True:
    try:
        job()
        sleep(300)
    except KeyboardInterrupt:
        exit()
    except Exception as e:
        Methods.log("UptimeParser-ERROR", f"Произошла ошибка.\n\n{e}")
        Methods.send(331465308, f"С uptime-парсером что-то не так!\n\n{e}")