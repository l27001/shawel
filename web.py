#!/usr/bin/python3
from flask import Flask, request, render_template
from datetime import datetime, timedelta
from methods import Methods

app = Flask(__name__,
    template_folder="web/templates/",
    static_folder="web/static/")

@app.errorhandler(403)
def err403(e):
    return (render_template('error.html', code=403,
        description="Доступ запрещён",
        full_description="У Вас нет прав доступа к этому объекту. \
        Файл недоступен для чтения, или сервер не может его прочитать."), 403)

@app.errorhandler(404)
def err404(e):
    return (render_template('error.html', code=404,
        description="Страница не найдена",
        full_description="Страница которую вы запросили не может быть найдена.\
        Возможна она была удалена или перемещена."), 404)

@app.errorhandler(405)
def err405(e):
    return (render_template('error.html', code=405,
        description="Method not allowed",
        full_description="That method is not allowed for the requested URL."), 405)

@app.route('/zvonki', methods=['GET'])
def zvonki():
    response = Methods.mysql_query("SELECT id FROM imgs WHERE mark='zvonki' ORDER BY id", fetch="all")
    if(len(response) > 0):
        rasp = []
        for n in response:
            rasp.append(n['id'])
    else:
        rasp = None
    # response = Methods.mysql_query("SELECT `rasp-checked`,`rasp-updated` FROM vk")
    return render_template('zvonki.html', title='Расписание звонков', rasp=rasp)

@app.route('/image/id_<id_>', methods=['GET'])
def getimg(id_):
    #id_ = request.args.get('id')
    if_mod = request.headers.get('If-Modified-Since')
    try:
        id_ = int(id_)
    except ValueError:
        return err404(404)
    if(if_mod != None and datetime.strptime(if_mod, "%a, %d %b %Y %H:%M:%S GMT") < datetime.now()+timedelta(seconds=14400)):
        return '', 304 #cached
    img = Methods.mysql_query("SELECT * FROM imgs WHERE id=%s", (id_))
    if(img == None):
        return err404(404)
    return (img['image'],
        200, {'Content-Type': f"image/{img['type']}",
            'Content-Size': img['size'],
            'Cache-Control': 'max-age=14400',
            'Last-Modified': datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            'Expires': (datetime.now()+timedelta(seconds=14400)).strftime("%a, %d %b %Y %H:%M:%S GMT")})

@app.route('/', methods=['GET'])
def index():
    response = Methods.mysql_query("SELECT id FROM imgs WHERE mark='rasp' ORDER BY id", fetch="all")
    if(len(response) > 0):
        rasp = []
        for n in response:
            rasp.append(n['id'])
    else:
        rasp = None
    response = Methods.mysql_query("SELECT `rasp-checked`,`rasp-updated` FROM vk")
    return render_template('index.html', title='Расписание', rasp=rasp, update=response)

if __name__ == '__main__':
    # app.run('192.168.1.6', port=5001, debug=True)
    from waitress import serve
    serve(app, host="127.0.0.1", port=5001)

