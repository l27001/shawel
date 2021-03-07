import re, requests, datetime, os, random, timeit, pymysql, pymysql.cursors
from other import api, dir_path, levels
import config

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36 OPR/70.0.3728.133'
}

class Methods:

	def make_button(color="primary",type="text",**kwargs):
		a = []
		for name,data in kwargs.items():
			a.append('"'+name+'":"'+str(data)+'"')
		kk = ",".join(a)
		if(type != "intent_unsubscribe" and type != "intent_subscribe"):
			return"{\"color\":\""+color+"\",\"action\":{\"type\":\""+type+"\","+kk+"}}"
		else:
			return"{\"action\":{\"type\":\""+type+"\","+kk+"}}"

	def construct_keyboard(inline="false",one_time="false",**kwargs):
		a = []
		for n in kwargs:
			a.append("["+kwargs[n]+"]")
		kx = f'"buttons":{a},"inline":{inline},"one_time":{one_time}'
		kx = '{'+kx+'}'
		return re.sub(r"[']",'',kx)

	def uptime():
		return requests.post('https://api.uptimerobot.com/v2/getMonitors', json={"api_key":config.uptimerobot_api}).json()

	def log(prefix,message,timestamp=True):
		if(os.path.isdir(dir_path+"/log/") == False):
			os.mkdir(dir_path+"/log")
		file = dir_path+"/log/"+datetime.datetime.today().strftime("%d.%m.%Y")+".log"
		if(timestamp == True):
			message = f"({datetime.datetime.today().strftime('%H:%M:%S')}) [{prefix}] {message}"
		else:
			message = f"[{prefix}] {message}"
		print(message)
		with open(file, 'a', encoding='utf-8') as f:
			f.write(message+"\n")

	def users_get(user_id,fields=''):
		try:
			return api.users.get(user_ids=user_id,fields=fields)
		except:
			return api.users.get(user_ids=user_id,fields=fields)

	def get_weather(location):
		resp = requests.get("https://api.openweathermap.org/data/2.5/weather?q="+location+"&appid=09ade3caac75957b990e25f6bb27b3f9&lang=ru&units=metric")
		return resp.json()

	def mysql_query(query,fetch="one",time=False):
		if(time == True):
			extime = timeit.default_timer()
		con = pymysql.connect(host=config.db['host'],
	        user=config.db['user'],
	        password=config.db['password'],
	        db=config.db['database'],
	        charset='utf8mb4',
	        autocommit=True,
	        cursorclass=pymysql.cursors.DictCursor)
		cur = con.cursor()
		cur.execute(query)
		if(fetch == "one"):
			data = cur.fetchone()
		else:
			data = cur.fetchall()
		con.close()
		if(time == True):
			Methods.log("Debug",f"Время запроса к MySQL: {str(timeit.default_timer()-extime)}")
		return data

	def send(peer_id,message='',attachment='',keyboard='',disable_mentions=0,intent="default"):
		return api.messages.send(peer_id=peer_id,random_id=random.randint(1,2147400000),message=message,attachment=attachment,keyboard=keyboard,disable_mentions=disable_mentions,intent=intent)

	def mass_send(peer_ids,message='',attachment='',keyboard='',disable_mentions=0):
		return api.messages.send(peer_ids=peer_ids,random_id=random.randint(1,2147400000),message=message,attachment=attachment,keyboard=keyboard,disable_mentions=disable_mentions)

	def upload_img(peer_id, file):
		if(Methods.is_message_allowed(peer_id) == 1):
			srvv = api.photos.getMessagesUploadServer(peer_id=peer_id)['upload_url']
		else:
			srvv = api.photos.getMessagesUploadServer(peer_id=331465308)['upload_url']
		no = requests.post(srvv, files={
					'file': open(file, 'rb')
				}).json()
		if(no['photo'] == '[]'):
			return 1
		response = api.photos.saveMessagesPhoto(photo=no['photo'],server=no['server'],hash=no['hash'])
		return f"photo{response[0]['owner_id']}_{response[0]['id']}_{response[0]['access_key']}"

	def download_img(url, file):
		p = requests.get(url, headers=headers)
		with open(file, "wb") as out:
			out.write(p.content)
		return file

	def upload_voice(peer_id,file):
		if(Methods.is_message_allowed(peer_id) == 1):
			url = api.docs.getMessagesUploadServer(type='audio_message',peer_id=peer_id)['upload_url']
		else:
			url = api.docs.getMessagesUploadServer(type='audio_message',peer_id=331465308)['upload_url']
		file = requests.post(url, files={
					'file': open(file, 'rb')
				}).json()['file']
		file = api.docs.save(file=file)
		return f"doc{file['audio_message']['owner_id']}_{file['audio_message']['id']}_{file['audio_message']['access_key']}"

	def is_message_allowed(id):
		return api.messages.isMessagesFromGroupAllowed(user_id=id,group_id=config.groupid)['is_allowed']

	def get_conversation_members(peer_id):
		try:
			return api.messages.getConversationMembers(group_id=config.groupid,peer_id=peer_id)['items']
		except Exception as e:
			if(e.code == 917):
				return 917

	def check_name(name):
		return api.utils.resolveScreenName(screen_name=name)

	def kick_user(chat,name):
		api.messages.removeChatUser(chat_id=chat-2000000000,member_id=name)

	def del_message(message_ids,delete_for_all=1,group_id=config.groupid):
		return api.messages.delete(message_ids=message_ids,delete_for_all=1,group_id=config.groupid)

	def set_typing(peer_id,type='typing',group_id=config.groupid):
		api.messages.setActivity(group_id=config.groupid,peer_id=peer_id,type=type)

	def get_level(expa):
		for name, expp in levels.items():
				if(expa-expp < 0):
					kx = {'name':name, 'exp':expp}
					return kx
		return {'name':'Легенда', 'exp':1000}
