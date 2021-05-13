#!/usr/bin/python3
from flask import Flask, jsonify, request, Response
import datetime
from collections import OrderedDict
from methods import Methods

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

def make_err_page(code, msg, path):
    return f"""<!DOCTYPE HTML>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{code} {msg}</title>
        </head>
        <body>
        <center><h1>Error {code}</h1><h2>{msg}</h2><h3>Path: {path}</h3><p></center>
        <hr>
        <em style="left: 15px; position: relative;">ShawelBot-API v1 </em></p>
        </body>
        </html>"""

def make_json_response(data_, args=None, status=1):
    if(status == 1):
        data = {"status":"ok"}
    elif(status == 0):
        data = {"status":"error"}
    if(args == None):
        data.update({'result':data_})
    else:
        get_args = {}
        for i in args:
            get_args.update({i: args[i]})
        data_.update({'get_args':get_args})
        data.update({'result':data_})
    data.update({'requested': datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")})
    return jsonify(data)

@app.errorhandler(404)
def err404(e):
    resp = make_json_response({'error':'Not Found', 'path':request.path}, request.args, 0)
    return resp, 404

@app.errorhandler(405)
def err405(e):
    resp = Response(make_err_page(405, "Method Not Allowed", request.path), 405)
    return resp

@app.route('/api/v1/parse/raspisanie/get', methods=['GET'])
def rasp_get():
    data = Methods.mysql_query("SELECT `rasp-updated`,`rasp-checked` FROM vk LIMIT 1")
    return make_json_response({'last-update':data['rasp-updated'],'last-checked':data['rasp-checked']})

@app.route('/api/v1/users/get/<id_>', methods=['GET'])
def user_get(id_):
    key = request.args.get('api-key')
    if(key == None):
        resp = make_json_response({'error':"Value 'api-key' must be passed",'path':request.path}, request.args, 0)
        return (resp, 400)
    data = Methods.mysql_query(f"SELECT key_ FROM api WHERE key_=%s LIMIT 1", (key))
    if(data == None):
        resp = make_json_response({'error':"Invalid 'api-key'",'path':request.path,'api-key':key}, request.args, 0)
        return (resp, 400)
    data = Methods.mysql_query(f"SELECT * FROM users WHERE vkid=%s LIMIT 1", (id_))
    if(data == None):
        resp = make_json_response({'error':"No user with this id",'path':request.path,'id':id_}, status=0)
        return (resp, 404)
    data_ = {}
    for i,j in data.items():
        data_.update({i:j})
    resp = make_json_response(data_)
    return resp

@app.route('/api/v1/users/get/', methods=['GET'])
@app.route('/api/v1/users/get', methods=['GET'])
def users_list():
    key = request.args.get('api-key')
    count = request.args.get('count')
    offset = request.args.get('offset')
    if(count == None):
        count = 20
    if(offset == None):
        offset = 0
    try: offset = int(offset)
    except ValueError:
        resp = make_json_response({'error':"Value 'offset' must be int",'path':request.path}, request.args, 0)
        return (resp, 400)
    try: count = int(count)
    except ValueError:
        resp = make_json_response({'error':"Value 'count' must be int",'path':request.path}, request.args, 0)
        return (resp, 400)
    if(key == None):
        resp = make_json_response({'error':"Value 'api-key' must be passed",'path':request.path}, request.args, 0)
        return (resp, 400)
    data = Methods.mysql_query(f"SELECT key_ FROM api WHERE key_=%s LIMIT 1", (key))
    if(data == None):
        resp = make_json_response({'error':"Invalid 'api-key'",'path':request.path,'api-key':key}, request.args, 0)
        return (resp, 400)
    data = Methods.mysql_query(f"SELECT * FROM users LIMIT %s OFFSET %s", (count, offset), fetch='all')
    resp = make_json_response({'count':count, 'offset':offset, 'users':{'count':len(data), 'list':data}})
    return resp

if __name__ == '__main__':
    app.run('192.168.1.111', debug=True)
    # from waitress import serve
    # serve(app, host="192.168.1.6", port=5000)

