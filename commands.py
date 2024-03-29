from os.path import isfile, isdir
from os import listdir, mkdir, remove
from collections import deque
import time, datetime, random, re, timeit, json

from config import groupid
from methods import Methods
from other import dir_path, blackwords
from demotivator.demotiv import demotiv
from voice.voice import mk_voice
import qiwi
from zerkalo.zerkalo import zerkalo
from text.text import text as mk_text
from parse import job as do_parse
from zvonki_parse import job as do_zvonki_parse

class Commands:

    def __init__(self, response):
        today = datetime.datetime.today()
        if(DEBUG == True):
            extime = timeit.default_timer()
            print(today.strftime("%H:%M:%S %d.%m.%Y")+ ": "+str(response))
        obj = response['object']['message']
        client_info = response['object']['client_info']
        if 'reply_message' in obj:
            replid = obj['reply_message']['from_id']
        else:
            replid = ''
        from_id = obj['from_id']
        chat_id = obj['peer_id']
        text = obj['text']
        if(from_id < 1 or text == ''):
            return None
        userr = Methods.users_get(from_id)
        userr = userr[0]['last_name']+" "+userr[0]['first_name']
        if(chat_id == from_id):
            who = f"от {userr}[{str(from_id)}]"
        else:
            who = f"в {str(chat_id)} от {userr}[{str(from_id)}]"
        userinfo = Mysql.query("SELECT * FROM users WHERE vkid='"+str(from_id)+"' LIMIT 1")
        if(userinfo == None):
            Mysql.query(f"INSERT INTO users (`vkid`) VALUES ('{from_id}')")
            userinfo = Mysql.query(f"SELECT * FROM users WHERE vkid='{from_id}' LIMIT 1")
        tlog = text.replace("\n",r" \n ")
        Methods.log("Message", f"'{tlog}' {who}")
        if(chat_id != from_id):
            curtime = int(time.time())
            m = Mysql.query(f"SELECT * FROM mute WHERE vkid = {from_id} AND chatid = {chat_id}")
            if(m != None):
                if(curtime > m['date']):
                    Mysql.query(f"DELETE FROM mute WHERE vkid = {from_id} AND chatid = {chat_id}")
                else:
                    if(m['warn']+1 < 3):
                        Mysql.query(f"UPDATE mute SET warn = warn + 1 WHERE vkid = {from_id} AND chatid = {chat_id}")
                        if(Methods.is_message_allowed(from_id) == 1):
                            Methods.send(from_id,f"Вам было выдано предупреждение за разговор в муте. [{m['warn']+1}/3]")
                        else:
                            Methods.send(chat_id,f"[id{from_id}|{userr}] было выдано предупреждение за разговор в муте. [{m['warn']+1}/3]")
                    else:
                        Methods.kick_user(chat_id,from_id)
                    return None
        if('payload' in obj):
            try:
                obj['payload'] = json.loads(obj['payload'])
                if('command' in obj['payload'] and obj['payload']['command'] == "internal_command"):
                    inline = Methods.check_keyboard(client_info['inline_keyboard'])
                    if(obj['payload']['action']['type'] == "intent_unsubscribe"):
                        Mysql.query(f"UPDATE users SET raspisanie='0' WHERE vkid='{from_id}'")
                        Methods.send(from_id, "Вы отписались от рассылки обновлений расписания.\nДля повторной подписки используйте команду '/рассылка'", keyboard=Methods.construct_keyboard(b1=Methods.make_button(type="intent_subscribe",peer_id=from_id,intent="non_promo_newsletter",label="Подписаться"),inline=inline))
                    elif(obj['payload']['action']['type'] == "intent_subscribe"):
                        Mysql.query(f"UPDATE users SET raspisanie='1' WHERE vkid='{from_id}'")
                        Methods.send(from_id, "Вы подписались на рассылку обновлений расписания.\nДля отписки используйте команду '/рассылка'", keyboard=Methods.construct_keyboard(b2=Methods.make_button(type="intent_unsubscribe",peer_id=from_id,intent="non_promo_newsletter",label="Отписаться"),inline=inline))
                    return None
            except TypeError: pass
            userinfo.update({'payload':obj['payload']})
        text = text.split(' ')
        if(re.match(rf"\[(club|public){groupid}\|(@|\*){scrname}\]", text[0])):
            text.pop(0)
        if(chat_id > 2000000000 and text[0][0] != '/'):
            if(text != []):
                if(Mysql.query("SELECT id FROM markov WHERE id = %s", (chat_id)) is None):
                    Mysql.query("INSERT INTO markov (`id`, `data`) VALUES (%s, %s)", (chat_id, " ".join(text)))
                else:
                    Mysql.query("UPDATE markov SET data = CONCAT(data, \" \", %s) WHERE id = %s", (" ".join(text), chat_id))
            return None
        elif(chat_id > 2000000000):
            chatinfo = Mysql.query(f"SELECT * FROM chats WHERE id = '{chat_id}' LIMIT 1")
            if(chatinfo == None):
                Mysql.query(f"INSERT INTO chats (`id`) VALUES ({chat_id})")
                chatinfo = Mysql.query(f"SELECT * FROM chats WHERE id = '{chat_id}' LIMIT 1")
            userinfo.update({'chatinfo':chatinfo})
        text[0] = text[0].lower()
        text[0] = text[0].replace('/','')
        userinfo.update({'replid':replid,'chat_id':chat_id, 'from_id':from_id, 'attachments':obj['attachments'], 'inline':client_info['inline_keyboard']})
        if(cmds.get(text[0]) == None):
            if(chat_id < 2000000000):
                Methods.send(chat_id, "👎🏻 Не понял.")
            return None
        else:
            try:
                cmds[text[0]](userinfo, text[1:])
            except Exception as e:
                Methods.log("ERROR", f"Непредвиденная ошибка. {str(e)}")
                Methods.send(chat_id, "⚠ Произошла непредвиденная ошибка.\nОбратитесь к @l27001", attachment="photo-183256712_457239188")
                raise e
        if(DEBUG == True):
            Methods.log("Debug", f"Время выполнения: {str(timeit.default_timer()-extime)}")

    def info(userinfo, text):
        """Выводит информацию о пользователе из БД. Если не указан пользователь, выведет информацию о текущем."""
        if(len(text) < 1):
            text.insert(0, str(userinfo['from_id']))
        t = re.findall(r'\[.*\|', text[0])
        try:
            t = t[0].replace("[", "").replace("|", "")
        except IndexError:
            t = text[0]
        if('payload' in userinfo):
            t = userinfo['payload']
        try:
            uinfo = Methods.users_get(t)
        except Exception as e:
            if(e.code == 113):
                Methods.send(userinfo['chat_id'], "⚠ Invalid user_id")
                return 0
        name = f"[id{uinfo[0]['id']}|{uinfo[0]['last_name']} {uinfo[0]['first_name']}]"
        uinfo = Mysql.query(f"SELECT * FROM users WHERE vkid='{uinfo[0]['id']}' LIMIT 1")
        if(uinfo == None):
            Methods.send(userinfo['chat_id'], "⚠ Пользователь не найден в БД")
            return 0
        if(uinfo['raspisanie'] == 0):
            raspisanie = 'Рассылка: Не подписан'
        else:
            raspisanie = 'Рассылка: Подписан'
        if(userinfo['chat_id'] != userinfo['from_id']):
            ch = f"\nChat-ID: {userinfo['chat_id']}"
        else:
            ch = ''
        keyb = Methods.construct_keyboard(b77=Methods.make_button(color="secondary", label="/get", payload=str(uinfo['vkid'])), b3=Methods.make_button(label="/полив", color="primary"), inline=Methods.check_keyboard(userinfo['inline']), b1=Methods.make_button(label="/топ", color="positive"), b2=Methods.make_button(label="/рассылка", color="secondary"))
        Methods.send(userinfo['chat_id'], "Имя: "+name+"\nVKID: "+str(uinfo['vkid'])+"\nDostup: "+str(uinfo['dostup'])+"\nEXP: "+str(uinfo['EXP'])+"\n"+raspisanie+ch, keyboard=keyb, disable_mentions=1)

    def time(userinfo, text):
        """Выводит текущее время"""
        Methods.send(userinfo['chat_id'], "🕒 Текущее серверное время "+datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')+"\nUnix-time: "+str(int(time.time())))

    def test(userinfo, text):
        """Тест"""
        Methods.send(userinfo['chat_id'], f"{scrname} by @l27001\nОбработано команд: {acmds}\nОшибок при выполнении команд: {aerrs}\nDebug: {DEBUG}\nЗапущен: {timestart.strftime('%Y-%m-%d %H:%M:%S')}\nВремя работы: {datetime.datetime.now()-timestart}", disable_mentions=1)

    def clrkeyb(userinfo, text):
        """"""
        Methods.send(userinfo['chat_id'], "Clear keyboard", keyboard='{"buttons":[]}')

    def random(userinfo, text):
        """Выбирает рандомное число из заданного промежутка"""
        if(len(text) < 2):
            Methods.send(userinfo['chat_id'], "⚠ /random [from] [to]")
        else:
            try:
                Methods.send(userinfo['chat_id'], "🎲 Выпало: "+str(random.randint(int(text[0]), int(text[1]))))
            except ValueError:
                Methods.send(userinfo['chat_id'], "⚠ /random [from] [to]")

    def vlaga(userinfo, text):
        """Проверить текущую влажность Щавеля"""
        vlaga = Mysql.query("SELECT vlaga FROM vk")['vlaga']
        Methods.send(userinfo['chat_id'], "Влажность Щавеля составляет "+str(vlaga)+"%")

    def weather(userinfo, text):
        """Проверяет погоду. Если не указан город, выведет погоду в Энгельсе"""
        if(len(text) < 1):
            a = "Энгельс"
        else:
            a = " ".join(text)
        weather = Methods.get_weather(a)
        if(weather['cod'] == "404"):
            Methods.send(userinfo['chat_id'], "⚠ Город "+a+" неизвестен серверу погоды.")
        elif(weather['cod'] != 200):
            Methods.send(userinfo['chat_id'], "⚠ Сервер погоды вернул некорректный ответ!")
        else:
            icon = weather['weather'][0]['icon']
            if(icon == '01d' or icon == '01n'):
                icon = "☀"
            elif(icon == '02d' or icon == '02n'):
                icon = "🌤"
            elif(icon == '03d' or icon == '03n'):
                icon = "☁"
            elif(icon == '04d' or icon == '04n'):
                icon = "☁"
            elif(icon == '09d' or icon == '09n'):
                icon = "🌧"
            elif(icon == '10d' or icon == '10n'):
                icon = "🌧"
            elif(icon == '11d' or icon == '11n'):
                icon = "🌩"
            elif(icon == '13d' or icon == '13n'):
                icon = "🌨"
            elif(icon == '50d' or icon == '50n'):
                icon = "🌫"
            Methods.send(userinfo['chat_id'], "Погода в "+weather['name']+"\n├ Местное время: "+datetime.datetime.utcfromtimestamp(weather['dt']+weather['timezone']).strftime('%Y-%m-%d %H:%M:%S')+"\n├ Статус: "+icon+" "+weather['weather'][0]['description']+"\n├ Температура: "+str(weather['main']['temp'])+" °С\n├ Ветер: "+str(weather['wind']['speed'])+" м/c\n├ Влажность: "+str(weather['main']['humidity'])+" %\n└ Давление: "+str(weather['main']['pressure']*100)+" Pa\nЗапрос сделан в "+datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'));

    def top(userinfo, text):
        """Выводит топ садовников"""
        data = Mysql.query("SELECT EXP, vkid FROM users WHERE vkid!='500136993' and EXP!=0 ORDER BY EXP DESC LIMIT 10", fetch='all')
        a = len(data)
        i = 1
        for n in data:
            if(i <= 1):
                ids = str(n['vkid'])
            else:
                ids = ids+","+str(n['vkid'])
            i+=1
        user = Methods.users_get(ids)
        txt = ''
        expa = []
        for n in data:
            kx = Methods.get_level(n['EXP'])
            expa.append(kx['name'])
        i = 0
        while(i < a):
            txt = txt+"\n"+str(i+1)+") [id"+str(user[i]['id'])+"|"+user[i]['last_name']+" "+user[i]['first_name']+"] ["+expa[i]+"]: "+str(data[i]['EXP'])+" EXP"
            i+=1
        keyb = Methods.construct_keyboard(b1=Methods.make_button(label="/полив", color="positive"), b4=Methods.make_button(label="/уровень", color="secondary"), b2=Methods.make_button(label="/влага", color="negative"), b3=Methods.make_button(label="/инфо", color="primary"), inline=Methods.check_keyboard(userinfo['inline']))
        Methods.send(userinfo['chat_id'], f"Топ садовников:{txt}", keyboard=keyb, disable_mentions=1)

    def poliv(userinfo, text):
        """Полей Щавеля!"""
        bd_inf = Mysql.query("SELECT vlaga,`time-poliv` FROM vk")
        if('chatinfo' in userinfo and userinfo['chatinfo']['game-cmds'] == 0):
            Methods.send(userinfo['chat_id'],"Данная команда отключена в этой беседе.")
            return 0
        timee = int(time.time())
        if(bd_inf['time-poliv']+300 < timee):
            if(bd_inf['vlaga'] == 100):
                Methods.send(userinfo['chat_id'], "Вы меня затопить хотите?")
            else:
                vl = random.randint(5, 15)
                if(vl+bd_inf['vlaga'] > 100):
                    vl = 100-bd_inf['vlaga']
                keyb = Methods.construct_keyboard(b1=Methods.make_button(label="/топ", color="positive"), b2=Methods.make_button(label="/влага", color="negative"), b3=Methods.make_button(label="/инфо", color="primary"), inline=Methods.check_keyboard(userinfo['inline']))
                Mysql.query(f"UPDATE users SET EXP=EXP+1 WHERE vkid='{userinfo['from_id']}'")
                Mysql.query("UPDATE vk SET `time-poliv`='"+str(timee)+"', `vlaga`='"+str(bd_inf['vlaga']+vl)+"'")
                Methods.send(userinfo['chat_id'], "Вы полили Щавеля.\nВлага: "+str(bd_inf['vlaga']+vl)+"%", keyboard=keyb)
                if(vl+bd_inf['vlaga'] == 100):
                    Methods.send(userinfo['chat_id'],"Влага достигла 100%. Вы получаете +10 бонусных EXP.")
                    Mysql.query(f"UPDATE users SET EXP=EXP+10 WHERE vkid='{userinfo['from_id']}'")
                i = 0
                kx = Methods.get_level(userinfo['EXP'])
                kx1 = Methods.get_level(userinfo['EXP']+1)
                if(kx['name'] != kx1['name']):
                    keyb=Methods.construct_keyboard(b1=Methods.make_button(label="/топ"), b2=Methods.make_button(label="/уровень", color="secondary"), inline=Methods.check_keyboard(userinfo['inline']))
                    Methods.send(userinfo['chat_id'], f"ТЫЩ! Вы получили новый уровень!\nНовый уровень: {kx1['name']}\nEXP: {userinfo['EXP']+1}", keyboard=keyb)
        else:
            t = 300-(timee-bd_inf['time-poliv'])
            m = t//60
            t = t-m*60
            tim = str(m)+" минут "+str(t)+" секунд"
            Methods.send(userinfo['chat_id'], "Поливать Щавеля можно раз в 5 минут!\nОсталось: "+tim)

    def raspisanie(userinfo, text):
        """Присылает последнее расписание"""
        rasp = Mysql.query("SELECT rasp FROM vk")['rasp']
        if(userinfo['raspisanie'] == 1 or userinfo['chat_id'] > 2000000000):
            text = "https://shawel.ezdomain.ru\n\nПоследнее расписание:"
            keyb = ''
        else:
            text = "https://shawel.ezdomain.ru\n\nВы можете подписаться на рассылку раписания с помощью кнопки ниже."
            keyb = Methods.construct_keyboard(b1=Methods.make_button(type="intent_subscribe",peer_id=userinfo['from_id'],intent="non_promo_newsletter",label="Подписаться"),inline=Methods.check_keyboard(userinfo['inline']))
        Methods.send(userinfo['chat_id'], text, rasp, keyboard=keyb)
        #Methods.send(userinfo['chat_id'], "Какое расписание? Каникулы...")

    def send(userinfo, text):
        """/send"""
        if(userinfo['dostup'] < 2):
            Methods.send(userinfo['chat_id'], "⛔ Не разрешено!")
        elif(len(text) < 2):
            Methods.send(userinfo['chat_id'], "⚠ /send [peer_id] [text]")                             
        else:
            try:
                int(text[0])
            except ValueError:
                Methods.send(userinfo['chat_id'], "⚠ /send [peer_id] [text]") 
            i = 0
            ttext = " ".join(text[1:])
            if(text[0] == '0'):
                text[0] = '2000000015'
            attach = ''
            if(len(userinfo['attachments']) >= 1):
                if(userinfo['attachments'][0]['type'] == 'wall'):
                    attach = "wall"+str(userinfo['attachments'][0]['wall']['to_id'])+"_"+str(userinfo['attachments'][0]['wall']['id'])
                else:
                    i = 0
                    for n in userinfo['attachments']:
                        typ = n['type']
                        if(i == 0):
                            attach = typ+str(n[typ]['owner_id'])+"_"+str(n[typ]['id'])+"_"+str(n[typ]['access_key'])
                        else:
                            attach = attach+','+typ+str(n[typ]['owner_id'])+"_"+str(n[typ]['id'])+"_"+str(n[typ]['access_key'])
                        i+=1
            try:
                Methods.send(text[0], ttext, attach)
                if(int(userinfo['chat_id']) != int(text[0])):
                    Methods.send(userinfo['chat_id'], "Сообщение было отправлено.")
            except Exception as e:
                if(e.code == 901):
                    Methods.send(userinfo['chat_id'], "⚠ Пользователь запретил отправку ему сообщений!")

    def rass(userinfo, text):
        """Подписаться/Отписаться от рассылки актуального расписания"""
        if(userinfo['chat_id'] == userinfo['from_id']):
            if(userinfo['raspisanie'] == 0):
                Methods.send(userinfo['chat_id'],"Вы не подписаны", keyboard=Methods.construct_keyboard(b1=Methods.make_button(type="intent_subscribe",peer_id=userinfo['from_id'],intent="non_promo_newsletter",label="Подписаться"),inline=Methods.check_keyboard(userinfo['inline'])))
            else:
                Methods.send(userinfo['chat_id'],"Вы подписаны", keyboard=Methods.construct_keyboard(b2=Methods.make_button(type="intent_unsubscribe",peer_id=userinfo['from_id'],intent="non_promo_newsletter",label="Отписаться"),inline=Methods.check_keyboard(userinfo['inline'])))
        else:
            count = Mysql.query(f"SELECT COUNT(*) FROM `chats` WHERE id = {userinfo['chat_id']} AND raspisanie=1")['COUNT(*)']
            if(count != 1):
                Mysql.query(f"UPDATE `chats` SET raspisanie=1 WHERE id='{userinfo['chat_id']}'")
                Methods.send(userinfo['chat_id'],"Вы подписали беседу на рассылку обновлений расписания.\nДля рассылки лично вам напишите боту в ЛС.")
            else:
                Mysql.query(f"UPDATE `chats` SET raspisanie=0 WHERE id='{userinfo['chat_id']}'")
                Methods.send(userinfo['chat_id'],"Вы отписали беседу от рассылки обновлений расписания.\nДля рассылки лично вам напишите боту в ЛС.")

    def log(userinfo, text):
        """"""
        if(userinfo['dostup'] < 2):
            Methods.send(userinfo['chat_id'], "⛔ Не разрешено!")
        else:
            with open(dir_path+"/log/"+datetime.datetime.today().strftime("%d.%m.%Y")+".log") as f:
                a = " ".join(list(deque(f, 10)))
            Methods.send(userinfo['chat_id'], a, disable_mentions=1)

    def get(userinfo, text):
        """Выводит информацию о любом пользователе ВКонтакте."""
        if(len(text) < 1):
            text.insert(0, str(userinfo['from_id']))
        t = re.findall(r'\[.*\|', text[0])
        try:
            t = t[0].replace("[","").replace("|","")
        except IndexError:
            t = text[0]
        if('payload' in userinfo):
            t = userinfo['payload']
        try:
            response = Methods.users_get(t, "sex,photo_id,bdate,online")
        except Exception as e:
            if(e.code == 113):
                Methods.send(userinfo['chat_id'], "⚠ Invalid user_id '"+str(t)+"'")
                return 0
        txt = ""
        for n in response[0]:
            txt = txt+str(n)+" => "+str(response[0][n])+"\n"
        try:
            img = "photo"+response[0]['photo_id']
        except Exception:
            img = ""
        keyb = Methods.construct_keyboard(b1=Methods.make_button(color="secondary", label="/info", payload=str(response[0]['id'])), b2=Methods.make_button(label="/топ"), inline=Methods.check_keyboard(userinfo['inline']))
        Methods.send(userinfo['chat_id'], txt+"vk.com/id"+str(response[0]['id']), img, keyboard=keyb)

    def demotiv(userinfo, text):
        """Генерирует демотиватор"""
        try:
            if(userinfo['attachments'][0]['type'] != 'photo'):
                Methods.send(userinfo['chat_id'], "⚠ Необходима фотография!\n\n/demotiv Строка 1(обязат)\nстрока 2(не обязат)")
            else:
                text = " ".join(text)
                text1 = ''
                text2 = ''
                if "\n" in text:
                    text1 = re.findall('.*\n', text)[0].replace("\n", "")
                    text2 = re.findall('\n.*', text)[0].replace("\n", "")
                elif "|" in text:
                    text1 = re.findall(r'.*\|', text)[0].replace("|", "")
                    text2 = re.findall(r'\|.*', text)[0].replace("|", "")
                else:
                    text1 = text
                height = 0
                width = 0
                for n in userinfo['attachments'][0]['photo']['sizes']:
                    if(n['height'] > height or n['width'] > width):
                        height = n['height']
                        width = n['width']
                        url = n['url']
                demot = demotiv(text1, text2, url)
                response = Methods.upload_img(userinfo['from_id'], demot)
                remove(demot)
                Methods.send(userinfo['chat_id'], "", response)
        except (KeyError, IndexError):
                Methods.send(userinfo['chat_id'], "⚠ Необходима фотография!\n\n/demotiv Строка 1(обязат)\nстрока 2(не обязат)")

    def help(userinfo, text):
        """Помощь"""
        a = ''
        lock = ['dlist', 'дедики', 'ddos', 'except']
        pred = 0
        for i,n in cmds.items():
            if(i in lock):
                pred = n
                continue
            if(n == pred):
                continue
            pred = n
            if(n.__doc__ == None or n.__doc__ == ''):
                doc = "Нет описания"
            else:
                doc = n.__doc__
            a = a +"\n/"+i+" - "+doc
        Methods.send(userinfo['chat_id'], a)

    def status(userinfo, text):
        """Статус"""
        response = Mysql.query("SELECT * FROM uptime WHERE status != '2' ORDER BY friendly_name", fetch="all")
        if(response == ()):
            Methods.send(userinfo['chat_id'], "✔ Все в порядке.")
        else:
            out = []
            for i in response:
                if(i['status'] == 9 or i['status'] == 8):
                    out.append(f"⚠ {i['friendly_name']} Недоступен!")
                elif(i['status'] == 0):
                    out.append(f"❓ {i['friendly_name']} Приостановлен")
                else:
                    out.append(f"❓ {i['friendly_name']} -> {i['status']}")
            Methods.send(userinfo['chat_id'], "\n".join(out))


    def aEXP(userinfo, text):
        """"""
        if(userinfo['dostup'] < 2):
            Methods.send(userinfo['chat_id'], "⛔ Не разрешено!")
        elif(len(text) < 2):
            Methods.send(userinfo['chat_id'], "⚠ /aEXP [userid] [(-)EXP]")
        else:
            t = re.findall(r'\[.*\|', text[0])
            try:
                t = t[0].replace("[", "").replace("|", "")
            except IndexError:
                t = text[0]
            try:
                unfo = Methods.users_get(t)
            except Exception as e:
                if(e.code == 113):
                    Methods.send(userinfo['chat_id'], "⚠ Invalid user_id")
                    return 0
            uinfo = Mysql.query(f"SELECT * FROM users WHERE vkid='{unfo[0]['id']}' LIMIT 1")
            if(uinfo == None):
                Methods.send(userinfo['chat_id'], "⚠ Пользователь не найден в БД")
            else:
                try:
                    text[1] = int(text[1])
                    if(text[1] < 0):
                        text[1] = str(text[1])
                        do = "Удалено"
                    elif(text[1] > 0):
                        text[1] = "+"+str(text[1])
                        do = "Добавлено"
                    else:
                        Methods.send(userinfo['chat_id'], "⚠ Введено не число")
                        return 0
                except ValueError:
                    Methods.send(userinfo['chat_id'], "⚠ Введено не число")
                    return 0
                Mysql.query("UPDATE users SET EXP=EXP"+text[1]+" WHERE vkid='"+str(uinfo['vkid'])+"' LIMIT 1")
                Methods.send(userinfo['chat_id'], "✔ "+do+" "+text[1]+" EXP пользователю "+unfo[0]['last_name']+" "+unfo[0]['first_name'])

    def spam(userinfo, text):
        """"""
        if(userinfo['dostup'] < 2):
            Methods.send(userinfo['chat_id'], "⛔ Не разрешено!")
        elif(len(text) < 2):
            Methods.send(userinfo['chat_id'], "⚠ /spam [peer_id] [text]")                             
        else:
            try:
                int(text[0])
            except ValueError:
                Methods.send(userinfo['chat_id'], "⚠ /spam [peer_id] [text]") 
            i = 0
            ttext = " ".join(text[1:])
            attach = ''
            if(len(userinfo['attachments']) >= 1):
                if(userinfo['attachments'][0]['type'] == 'wall'):
                    attach = "wall"+str(userinfo['attachments'][0]['wall']['to_id'])+"_"+str(userinfo['attachments'][0]['wall']['id'])
                else:
                    i = 0
                    for n in userinfo['attachments']:
                        typ = n['type']
                        if(i == 0):
                            attach = typ+str(n[typ]['owner_id'])+"_"+str(n[typ]['id'])+"_"+str(n[typ]['access_key'])
                        else:
                            attach = attach+','+typ+str(n[typ]['owner_id'])+"_"+str(n[typ]['id'])+"_"+str(n[typ]['access_key'])
                        i+=1
            try:
                for i in  range(10):
                    Methods.send(text[0], ttext, attach)
                if(int(userinfo['chat_id']) != int(text[0])):
                    Methods.send(userinfo['chat_id'], "Сообщение было отправлено.")
            except Exception as e:
                if(e.code == 901):
                    Methods.send(userinfo['chat_id'], "⚠ Пользователь запретил отправку ему сообщений!")

    def nul(userinfo, text):
        """"""
        if(userinfo['dostup'] < 2):
            Methods.send(userinfo['chat_id'], "⛔ Не разрешено!")
        else:
            Mysql.query("UPDATE `vk` SET `time-poliv`=3")
            Methods.send(userinfo['chat_id'], "✔ Success!")

    def level(userinfo, text):
        """Проверяет ваш текущий уровень"""
        kx = Methods.get_level(userinfo['EXP'])
        lvl = kx['name']
        lvlnext = kx['exp']
        nexp = lvlnext - userinfo['EXP']
        keyb = Methods.construct_keyboard(inline=Methods.check_keyboard(userinfo['inline']), b1=Methods.make_button(label="/топ", color="positive"), b2=Methods.make_button(label="/инфо"))
        Methods.send(userinfo['chat_id'], f"🏅 Ваш уровень: {lvl}\nEXP: {userinfo['EXP']}\nСледующий уровень через {nexp} EXP", keyboard=keyb)

    def autopoliv(userinfo, text):
        """Прекращает процесс высыхания Щавеля на определённое время"""
        autopoliv = Mysql.query("SELECT autopoliv FROM vk")['autopoliv']
        timee = int(time.time())
        if(autopoliv >= timee):
            Methods.send(userinfo['chat_id'], "⚠ Автополив уже активен.")
        else:
            if(len(text) < 1):
                Methods.send(userinfo['chat_id'], "ℹ Автополив.\nИспользование: /автополив [кол-во часов]\nЩавель не будет высыхать указанное кол-во часов.\n1 час автополива = 20 EXP.")
            else:
                try:
                    n = int(text[0])
                except ValueError:
                    Methods.send(userinfo['chat_id'], "⚠ Введено не число.")
                if(n < 1 or n > 12):
                    Methods.send(userinfo['chat_id'], "⚠ Допустимы значения от 1 до 12 часов.")
                else:
                    if(userinfo['EXP'] < n*20):
                        Methods.send(userinfo['chat_id'], "⚠ Недостаточно EXP!")
                    else:
                        d = timee+3600*n
                        pr = time.strftime("%H:%M", time.localtime(d))
                        Mysql.query(f"UPDATE vk SET autopoliv={d}")
                        Mysql.query(f"UPDATE users SET `EXP`=`EXP`-{n*20} WHERE vkid={userinfo['from_id']}")
                        keyb = Methods.construct_keyboard(inline=Methods.check_keyboard(userinfo['inline']), b1=Methods.make_button(label="/топ", color="positive"), b2=Methods.make_button(label="/полив"), b3=Methods.make_button(color="secondary", label="/влага"))
                        Methods.send(userinfo['chat_id'], f"✔ Вы активировали автополив на {n} часов.\nАвтополив будет активен до {pr}.\nСписано {n*20} EXP", keyboard=keyb)

    def kazik(userinfo, text):
        """Казино"""
        if('chatinfo' in userinfo and userinfo['chatinfo']['game-cmds'] == 0):
            Methods.send(userinfo['chat_id'],"Данная команда отключена в этой беседе.")
            return 0
        if(len(text) < 2):
            Methods.send(userinfo['chat_id'], "⚠ /казино [ставка] [1/2]\n\n1 - Выпадет число от 1 до 100\n2 - Выпадет число от 101 до 200")
            return 0
        try:
            stav = int(text[0])
            if(stav < 1):
                raise ValueError
            y = int(text[1])
            if(y < 1 or y > 2):
                raise ValueError
        except ValueError:
            Methods.send(userinfo['chat_id'], "⚠ Введите число. /казино [ставка] [1/2]\n\n1 - Выпадет число от 1 до 100\n2 - Выпадет число от 101 до 200")
            return 0
        if(stav < 5 and userinfo['EXP'] > 5):
            Methods.send(userinfo['chat_id'],"⚠ Ставка не может быть меньше 5-ти.")
            return 0
        if(stav > userinfo['EXP']):
            Methods.send(userinfo['chat_id'], f"⚠ У вас нет столько EXP.\nВаши EXP {userinfo['EXP']}")
            return 0
        if(userinfo['dostup'] > 0 and len(text) >= 3):
            try:
                win = int(text[2])
                if(win < 1 or win > 200): raise ValueError
            except ValueError:
                win = random.randint(1, 200)
        else:
            win = random.randint(1, 200)
        tt = f"\nВыпало {win}."
        keyb = Methods.construct_keyboard(b1=Methods.make_button(color="secondary", label="/уровень"), b2=Methods.make_button(color="secondary", label="/топ"), inline=Methods.check_keyboard(userinfo['inline']))
        if((win <= 100 and y == 2) or (win >= 101 and y == 1)):
            Methods.send(userinfo['chat_id'], f"Вы проиграли {stav} EXP.{tt}\nВаши EXP {userinfo['EXP']-stav}.", keyboard=keyb)
            Mysql.query(f"UPDATE users SET `EXP`=`EXP`-{stav} WHERE vkid={userinfo['from_id']}")
        else:
            Methods.send(userinfo['chat_id'], f"Вы выйграли {stav} EXP.{tt}\nВаши EXP {userinfo['EXP']+stav}.", keyboard=keyb)
            Mysql.query(f"UPDATE users SET `EXP`=`EXP`+{stav} WHERE vkid={userinfo['from_id']}")

    def say(userinfo, text):
        """Скажи ...."""
        if(len(text) < 1):
            Methods.send(userinfo['chat_id'], "/say [text]")
            return 0
        ttext = [item.lower() for item in text]
        cc = list(set(ttext) & set(blackwords))
        if(len(cc) > 0):
            Methods.send(userinfo['chat_id'], "⚠ Так нельзя говорить.")
            return 0
        text = " ".join(text)
        Methods.send(userinfo['chat_id'], text)

    def voice(userinfo, text):
        """Озвучить текст"""
        if(len(text) < 1):
            Methods.send(userinfo['chat_id'], "/voice [text]")
            return 0
        ttext = [item.lower() for item in text]
        cc = list(set(ttext) & set(blackwords))
        if(len(cc) > 0):
            Methods.send(userinfo['chat_id'], "⚠ Так нельзя говорить.")
            return 0
        text = " ".join(text)
        if(len(text) > 400):
            Methods.send(userinfo['chat_id'], "⚠ Слишком много символов (более 400)")
            return 0
        Methods.set_typing(userinfo['chat_id'],type_='audiomessage')
        try:
            file = mk_voice(text)
        except AssertionError:
            Methods.send(userinfo['chat_id'],"⚠ Введен некорректный текст для озвучивания.")
            return 0
        file_send = Methods.upload_voice(userinfo['from_id'], file)
        remove(file)
        Methods.send(userinfo['chat_id'], attachment=file_send)

    def setdostup(userinfo, text):
        """"""
        if(userinfo['dostup'] < 2 and userinfo['from_id'] != 331465308):
            Methods.send(userinfo['chat_id'], "⛔ Не разрешено!")
        elif(len(text) < 2):
            Methods.send(userinfo['chat_id'], "⚠ /setdostup [userid] [dostup]")
        else:
            t = re.findall(r'\[.*\|', text[0])
            try:
                t = t[0].replace("[", "").replace("|", "")
            except IndexError:
                t = text[0]
            try:
                unfo = Methods.users_get(t)
            except Exception as e:
                if(e.code == 113):
                    Methods.send(userinfo['chat_id'], "⚠ Invalid user_id")
                    return 0
            uinfo = Mysql.query(f"SELECT * FROM users WHERE vkid='{unfo[0]['id']}' LIMIT 1")
            if(uinfo == None):
                Methods.send(userinfo['chat_id'], "⚠ Пользователь не найден в БД")
            else:
                try:
                    text[1] = int(text[1])
                    if(text[1] < 0):
                        Methods.send(userinfo['chat_id'],"⚠ Доступ не может быть больее 2 или менее 0")
                        return 0
                    elif(text[1] > 2):
                        Methods.send(userinfo['chat_id'],"⚠ Доступ не может быть более 2 или менее 0")
                        return 0
                except ValueError:
                    Methods.send(userinfo['chat_id'], "⚠ Введено не число")
                    return 0
                Mysql.query("UPDATE users SET dostup="+str(text[1])+" WHERE vkid='"+str(uinfo['vkid'])+"' LIMIT 1")
                Methods.send(userinfo['chat_id'], f"✔ Установлен уровень доступа {text[1]} пользователю {unfo[0]['last_name']} {unfo[0]['first_name']}")

    def kick(userinfo, text):
        """Кикнуть пользователя из беседы"""
        k = Methods.get_conversation_members(userinfo['chat_id'])
        if(k == 917):
            Methods.send(userinfo['chat_id'],"⚠ У меня нет доступа администратора.")
            return 0
        for n in k:
            if(n['member_id'] == userinfo['from_id']):
                admin = 0
                if 'is_admin' in n:
                    admin = 1
                    break
        if(userinfo['dostup'] < 2 and admin == 0):
            Methods.send(userinfo['chat_id'],"⛔ Нет доступа")
            return 0
        if(userinfo['chat_id'] < 2000000000):
            Methods.send(userinfo['chat_id'],"⚠ Это не беседа.")
            return 0
        if(userinfo['replid'] == '' and len(text) < 1):
            Methods.send(userinfo['chat_id'],"⚠ Укажите пользователя или ответьте на сообщение.")
            return 0
        elif(userinfo['replid'] == '' and len(text) >= 1):
            t = re.findall(r'\[.*\|', text[0])
            try:
                t = t[0].replace("[","").replace("|","")
            except IndexError:
                t = text[0]
            if('payload' in userinfo):
                t = userinfo['payload']
            check = Methods.check_name(t)
            try:
                if(check['type'] == 'group'):
                    replid = int(f"-{check['object_id']}")
                else:
                    replid = check['object_id']
            except (KeyError,TypeError):
                replid = t
        else:
            replid = userinfo['replid']
        s = 0
        for n in k:
            if(n['member_id'] == replid):
                if 'is_admin' in n:
                    Methods.send(userinfo['chat_id'],"⚠ Этого человека нельзя кикнуть.")
                    return 0
                s = 1
                break
        if(s != 1):
            Methods.send(userinfo['chat_id'],"⚠ Этого человека нет в беседе.")
            return 0
        if(replid == groupid or replid == userinfo['from_id'] or replid == int(f"-{groupid}")):
            Methods.send(userinfo['chat_id'],"⚠ Этого человека нельзя кикнуть.")
            return 0
        Methods.kick_user(userinfo['chat_id'],replid)

    def unmute(userinfo, text):
        """Размутить пользователя"""
        k = Methods.get_conversation_members(userinfo['chat_id'])
        if(k == 917):
            Methods.send(userinfo['chat_id'],"⚠ У меня нет доступа администратора.")
            return 0
        for n in k:
            if(n['member_id'] == userinfo['from_id']):
                admin = 0
                if 'is_admin' in n:
                    admin = 1
                    break
        if(userinfo['dostup'] < 2 and admin == 0):
            Methods.send(userinfo['chat_id'],"⛔ Нет доступа")
            return 0
        if(userinfo['chat_id'] < 2000000000):
            Methods.send(userinfo['chat_id'],"⚠ Это не беседа.")
            return 0
        if(userinfo['replid'] == '' and len(text) < 1):
            Methods.send(userinfo['chat_id'],"⚠ Укажите пользователя или ответьте на сообщение и укажите время в минутах.")
            return 0
        elif(userinfo['replid'] == '' and len(text) >= 1):
            t = re.findall(r'\[.*\|', text[0])
            try:
                t = t[0].replace("[","").replace("|","")
            except IndexError:
                t = text[0]
            if('payload' in userinfo):
                t = userinfo['payload']
            check = Methods.check_name(t)
            try:
                if(check['type'] == 'group'):
                    replid = int(f"-{check['object_id']}")
                else:
                    replid = check['object_id']
            except (KeyError,TypeError):
                replid = t
            del(text[0])
        else:
            replid = userinfo['replid']
        s = 0
        if(len(text) == 0):
            mt = 5
        elif(len(text) >= 1):
            try:
                mt = int(text[0])
            except ValueError:
                mt = 5
        if(mt > 180 or mt < 1):
            mt = 180
        mt = mt * 60
        for n in k:
            if(n['member_id'] == replid):
                if 'is_admin' in n:
                    Methods.send(userinfo['chat_id'],"⚠ Этого человека нельзя замутить.")
                    return 0
                s = 1
                break
        if(s != 1):
            Methods.send(userinfo['chat_id'],"⚠ Этого человека нет в беседе.")
            return 0
        if(replid == groupid or replid == userinfo['from_id'] or replid == int(f"-{groupid}")):
            Methods.send(userinfo['chat_id'],"⚠ Этого человека нельзя замутить.")
            return 0
        m = Mysql.query(f"SELECT * FROM mute WHERE vkid = {replid} AND chatid = {userinfo['chat_id']}",fetch='all')
        curtime = int(time.time())
        if(len(m) == 0):
            Methods.send(userinfo['chat_id'],"Этот человек не в муте.")
            return 0
        Mysql.query(f"DELETE FROM mute WHERE chatid = {userinfo['chat_id']} AND vkid = {replid}")
        Methods.send(userinfo['chat_id'],f"✔ Пользователю [id{replid}|{replid}] снят мут.")

    def mute(userinfo, text):
        """Замутить пользователя"""
        k = Methods.get_conversation_members(userinfo['chat_id'])
        if(k == 917):
            Methods.send(userinfo['chat_id'],"⚠ У меня нет доступа администратора.")
            return 0
        for n in k:
            if(n['member_id'] == userinfo['from_id']):
                admin = 0
                if 'is_admin' in n:
                    admin = 1
                    break
        if(userinfo['dostup'] < 2 and admin == 0):
            Methods.send(userinfo['chat_id'],"⛔ Нет доступа")
            return 0
        if(userinfo['chat_id'] < 2000000000):
            Methods.send(userinfo['chat_id'],"⚠ Это не беседа.")
            return 0
        if(userinfo['replid'] == '' and len(text) < 1):
            Methods.send(userinfo['chat_id'],"⚠ Укажите пользователя или ответьте на сообщение и укажите время в минутах.")
            return 0
        elif(userinfo['replid'] == '' and len(text) >= 1):
            t = re.findall(r'\[.*\|', text[0])
            try:
                t = t[0].replace("[","").replace("|","")
            except IndexError:
                t = text[0]
            if('payload' in userinfo):
                t = userinfo['payload']
            check = Methods.check_name(t)
            try:
                if(check['type'] == 'group'):
                    replid = int(f"-{check['object_id']}")
                else:
                    replid = check['object_id']
            except (KeyError,TypeError):
                replid = t
            del(text[0])
        else:
            replid = userinfo['replid']
            s = 0
        if(len(text) == 0):
            mt = 5
        elif(len(text) >= 1):
            try:
                mt = int(text[0])
            except ValueError:
                mt = 5
        if(mt > 180 or mt < 1):
            mt = 5
        mt = mt * 60
        for n in k:
            if(n['member_id'] == replid):
                if 'is_admin' in n:
                    Methods.send(userinfo['chat_id'],"⚠ Этого человека нельзя замутить.")
                    return 0
                s = 1
                break
        if(s != 1):
            Methods.send(userinfo['chat_id'],"⚠ Этого человека нет в беседе.")
            return 0
        if(replid == groupid or replid == userinfo['from_id'] or replid == int(f"-{groupid}")):
            Methods.send(userinfo['chat_id'],"⚠ Этого человека нельзя замутить.")
            return 0
        m = Mysql.query(f"SELECT * FROM mute WHERE vkid = {replid} AND chatid = {userinfo['chat_id']}",fetch='all')
        curtime = int(time.time())
        if(len(m) >= 1):
            if(curtime <= m[0]['date']):
                Methods.send(userinfo['chat_id'],"Этот человек уже в муте.")
                return 0
            else:
                Mysql.query(f"DELETE FROM mute WHERE chatid = {userinfo['chat_id']} AND vkid = {replid}")
        Mysql.query(f"INSERT INTO mute (chatid,vkid,date) VALUES ({userinfo['chat_id']},{replid},{curtime+mt})")
        Methods.send(userinfo['chat_id'],f"✔ Пользователю [id{replid}|{replid}] выдан мут на {mt} секунд.")

    def switch_game(userinfo, text):
        """Включает/Отключает развлекательные команды (полив, казино) в беседе"""
        if(userinfo['chat_id'] == userinfo['from_id']):
            Methods.send(userinfo['chat_id'],"⚠ Эта команда доступна только в беседе.")
            return 0
        k = Methods.get_conversation_members(userinfo['chat_id'])
        if(k != 917):
            for n in k:
                if(n['member_id'] == userinfo['from_id']):
                    admin = 0
                    if 'is_admin' in n:
                        admin = 1
                        break
        else:
            admin = 0
        if(userinfo['dostup'] < 2 and admin == 0):
            Methods.send(userinfo['chat_id'],"⛔ Нет доступа")
            return 0
        if(userinfo['chatinfo']['game-cmds'] == 0):
            Mysql.query(f"UPDATE chats SET `game-cmds`=1 WHERE id={userinfo['chat_id']}")
            Methods.send(userinfo['chat_id'],"⚠ Развлекательные команды включены.")
        else:
            Mysql.query(f"UPDATE chats SET `game-cmds`=0 WHERE id={userinfo['chat_id']}")
            Methods.send(userinfo['chat_id'],"⚠ Развлекательные команды отключены.")

    def qiwi_create(userinfo, text):
        """"""
        if(userinfo['dostup'] < 2):
            Methods.send(userinfo['chat_id'],"⛔ Нет доступа")
            return 0
        if(len(text) < 1):
            Methods.send(userinfo['chat_id'],"/qpay [sum] [comment]")
            return 0
        try:
            summ = int(text[0])
            if(summ < 1): raise ValueError
        except ValueError:
            Methods.send(userinfo['chat_id'],"Сумма должна быть положительным числом!")
            return 0
        result = qiwi.create_pay(summ,' '.join(text[1:]))
        Methods.send(userinfo['chat_id'],f"Ссылка создана.\nID: {result['id']}\nSum: {result['amount']}\nComment: {result['comment']}\n\n{result['url']}")

    def qiwi_check(userinfo, text):
        """"""
        if(userinfo['dostup'] < 2):
            Methods.send(userinfo['chat_id'],"⛔ Нет доступа")
            return 0
        if(len(text) < 1):
            Methods.send(userinfo['chat_id'],"/qcheck [bill id]")
            return 0
        try:
            result = qiwi.check_pay(text[0])
        except:
            Methods.send(userinfo['chat_id'], "Что-то пошло не так. Проверьте ID. Если все верно обратитесь к логам.")
            return 0
        Methods.send(userinfo['chat_id'],f"Comment: {result['comment']}\nStatus: {result['status']}\nSum: {result['amount']}")

    def qiwi_revoke(userinfo, text):
        """"""
        if(userinfo['dostup'] < 2):
            Methods.send(userinfo['chat_id'],"⛔ Нет доступа")
            return 0
        if(len(text) < 1):
            Methods.send(userinfo['chat_id'],"/qrevoke [bill-id]")
            return 0
        try:
            qiwi.revoke_pay(text[0])
        except:
            Methods.send(userinfo['chat_id'], "Что-то пошло не так. Проверьте ID. Если все верно обратитесь к логам.")
            return 0
        Methods.send(userinfo['chat_id'],"Revoked")

    def meme(userinfo, text):
        """Отправляет рандомный мемес из сохраненных"""
        imgs = sorted(listdir(f"{dir_path}/meme"))
        it = random.randint(1,len(imgs)-1)
        im = Methods.upload_img(userinfo['from_id'], f"{dir_path}/meme/{imgs[it]}")
        Methods.send(userinfo['chat_id'],f"{imgs[it].split('.')[0]}",attachment=im)

    def addmeme(userinfo, text):
        """Сохраняет прикрёпленные изображения в качестве мемесов"""
        if(isdir(f"{dir_path}/meme" == False)):
            mkdir(f"{dir_path}/meme")
        k = []
        for n in userinfo['attachments']:
            if(n['type'] != 'photo'):
                Methods.send(userinfo['chat_id'], "Нужна фотография!")
                return 0
            height = 0
            width = 0
            for n in n['photo']['sizes']:
                if(n['height'] > height or n['width'] > width):
                    height = n['height']
                    width = n['width']
                    url = n['url']
            k.append(url)
        if(len(k) == 0):
            Methods.send(userinfo['chat_id'], "Нужна фотография!")
            return 0
        for n in k:
            Methods.download_img(n,f"{dir_path}/meme/{random.randint(99999,99999999)}.jpg")
        Methods.send(userinfo['chat_id'],f"Добавлено {len(k)} memes'ов")

    def zvonki(userinfo, text):
        """Отправляет расписание звонков"""
        Methods.send(userinfo['chat_id'],"https://shawel.ezdomain.ru/zvonki",attachment=Mysql.query("SELECT zvonki FROM vk")['zvonki'])

    def zerkalo(userinfo, text):
        """Отзеркаливает изображение"""
        k = []
        typ = 1
        if(len(text) > 0):
            if(text[0] == "1"):
                typ = 2
        for n in userinfo['attachments']:
            if(n['type'] != 'photo'):
                Methods.send(userinfo['chat_id'], "Нужна фотография!")
                return 0
            height = 0
            width = 0
            for n in n['photo']['sizes']:
                if(n['height'] > height or n['width'] > width):
                    height = n['height']
                    width = n['width']
                    url = n['url']
            k.append(url)
        if(len(k) == 0):
            Methods.send(userinfo['chat_id'], "Нужна фотография!")
            return 0
        out = []
        for n in k:
            file = zerkalo(n, typ)
            out.append(Methods.upload_img(userinfo['from_id'], file))
            remove(file)
        Methods.send(userinfo['chat_id'], attachment=out)

    def text(userinfo, text):
        """Вставляет текст внизу изображения"""
        if(len(text) == 0):
            Methods.send(userinfo['chat_id'], "/text [текст]\nНеобходима фотография")
            return 0
        text = " ".join(text)
        k = []
        for n in userinfo['attachments']:
            if(n['type'] != 'photo'):
                Methods.send(userinfo['chat_id'], "Нужна фотография!")
                return 0
            height = 0
            width = 0
            for n in n['photo']['sizes']:
                if(n['height'] > height or n['width'] > width):
                    height = n['height']
                    width = n['width']
                    url = n['url']
            k.append(url)
        if(len(k) == 0):
            Methods.send(userinfo['chat_id'], "Нужна фотография!")
            return 0
        out = []
        for n in k:
            file = mk_text(n, text)
            out.append(Methods.upload_img(userinfo['from_id'], file))
            remove(file)
        Methods.send(userinfo['chat_id'], attachment=out)

    def do_parse(userinfo, text):
        if(userinfo['dostup'] < 2):
            Methods.send(userinfo['chat_id'], "⛔ Не разрешено!")
            return 0
        if(len(text) > 0):
            do_zvonki_parse()
        else:
            do_parse()

    def do_parse_quiet(userinfo, text):
        if(userinfo['dostup'] < 2):
            Methods.send(userinfo['chat_id'], "⛔ Не разрешено!")
            return 0
        if(len(text) > 0):
            do_zvonki_parse(1)
        else:
            do_parse(1)

cmds = {'info':Commands.info, 'инфо':Commands.info, 
'рандом':Commands.random, 'random':Commands.random, 
'time':Commands.time, 'время':Commands.time, 
'test':Commands.test, 'тест':Commands.test, 
'влага':Commands.vlaga, 'влажность':Commands.vlaga, 
'погода':Commands.weather, 'weather':Commands.weather, 
'топ':Commands.top, 
'полив':Commands.poliv, 'полить':Commands.poliv, 
'расписание':Commands.raspisanie, 
'send':Commands.send, 
'рассылка':Commands.rass, 'подписаться':Commands.rass, 'отписаться':Commands.rass,
'log':Commands.log, 'лог':Commands.log, 
'get':Commands.get, 
'demotiv':Commands.demotiv,'dem':Commands.demotiv,'демотиватор':Commands.demotiv, 
'help':Commands.help, 'помощь':Commands.help, 
'status':Commands.status, 'статус':Commands.status, 
'aexp':Commands.aEXP, 
'spam':Commands.spam, 'спам':Commands.spam, 
'null':Commands.nul, 'обнулить':Commands.nul, 
'akey':Commands.clrkeyb, 
'уровень':Commands.level, 'level':Commands.level, 'lvl':Commands.level, 'левел':Commands.level, 'лвл':Commands.level, 
'автополив':Commands.autopoliv, 
'казино':Commands.kazik, 
'say':Commands.say, 'скажи':Commands.say, 'напиши':Commands.say, 
'voice':Commands.voice, 'озвучить':Commands.voice, 'голос':Commands.voice,
'setdostup':Commands.setdostup,'dostup':Commands.setdostup,
'kick':Commands.kick,'кик':Commands.kick,
'mute':Commands.mute,'мут':Commands.mute,
'unmute':Commands.unmute,'размуть':Commands.unmute,'размутить':Commands.unmute,
'games':Commands.switch_game,
"qpay":Commands.qiwi_create,"qcheck":Commands.qiwi_check,"qrevoke":Commands.qiwi_revoke,
"meme":Commands.meme,
"addmeme":Commands.addmeme,
"звонки":Commands.zvonki,
"зеркало":Commands.zerkalo,"зер":Commands.zerkalo,
"text":Commands.text,"текст":Commands.text,
"парсер":Commands.do_parse,"парсерт":Commands.do_parse_quiet,
}
