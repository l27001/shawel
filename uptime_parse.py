#!/usr/bin/python3
import requests
from time import sleep
from methods import Methods
from config import uptimerobot_api

def check_status(status, name):
    if(status == 9 or status == 8):
        return f"⚠ {name} Недоступен!"
    elif(status == 0):
        return f"❓ {name} Приостановлен"
    elif(status == 2):
        return f"✅ {name} Доступен"
    else:
        return f"❓ {name} -> {status}"

def job():
    res = requests.post('https://api.uptimerobot.com/v2/getMonitors?format=json', json={"api_key":uptimerobot_api})
    if(res.status_code != 200):
        return True
    res = res.json()
    monitors = res['monitors']
    stat = []
    allu = Mysql.query("SELECT id, friendly_name FROM uptime ORDER BY friendly_name", fetch="all")
    all_mon = {}
    for k in allu:
        all_mon.update({k['id']:k['friendly_name']})
    for k in monitors:
        data = Mysql.query(f"SELECT * FROM uptime WHERE id='{k['id']}'")
        if(data == None):
            Mysql.query(f"INSERT INTO uptime (`id`,`friendly_name`,`status`) VALUES ('{k['id']}','{k['friendly_name']}','{k['status']}')")
            stat.append(check_status(k['status'], k['friendly_name']))
            continue
        elif(data['status'] != k['status'] or data['friendly_name'] != k['friendly_name']):
            Mysql.query(f"UPDATE uptime SET status='{k['status']}', friendly_name='{k['friendly_name']}' WHERE id='{k['id']}'")
            stat.append(check_status(k['status'], k['friendly_name']))
        all_mon.pop(k['id'])
    for id_, name in all_mon.items():
        stat.append(f"{name} Удалён")
        Mysql.query(f"DELETE FROM uptime WHERE id='{id_}'")
    text = "\n".join(stat)
    if(len(text) > 0):
        Methods.send(331465308, text)

if(__name__ == "__main__"):
    while True:
        Mysql = Methods.Mysql()
        try:
            job()
            sleep(300)
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            Methods.log("UptimeParser-ERROR", f"Произошла ошибка.\n\n{e}")
            Methods.send(331465308, f"С uptime-парсером что-то не так!\n\n{e}")
            sleep(300)
        finally:
            Mysql.close()
