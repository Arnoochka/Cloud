from flask import Flask
from flask import request
from flask import abort
import os
import multiprocessing as mp
import psycopg2 as psql
import json
import requests as reqs
from constants import DATA_SERVERS
from random import choice

app = Flask(__name__)
controller_token = 'CTRL_TOKEN'  # storing here is unsafe

# connection with PSQL at localhost
conn = psql.connect(user='fuck',
                    password='fuck',
                    host='127.0.0.1',
                    port=5432)

'''
POST Request
Only for copy_center's requests
Uses to say that username-filename copied to some disk_server, then
    controller must write new disk_server in psql
Returns:
    error: None

Parameters: encoded copy center's token, username, filename, data_host, data_port
'''
@app.route('/write_disk', methods=['POST'])
def handleCopyCenterRequest():
    if request.method != 'POST':
        return {
            'error': 'Undefinded'
        }
    
    # asure request is correct
    if not ('token' in request.files \
        and 'username' in request.files \
        and RequestUploadData.is_exist_filename_and_url(request.files)):
        return {
            'error': 'Bad request'
        }

    token = request.files['token'].stream.read().decode()
    filename = request.files['filename'].stream.read().decode()
    username = request.files['username'].stream.read().decode()
    host = request.files['data_host'].stream.read().decode()
    port = request.files['data_port'].stream.read().decode()

    query = "SELECT * FROM viktor_files WHERE username=%s AND filename=%s"
    cur = conn.cursor()
    cur.execute(query, [username, filename])
    rows = list(cur.fetchall())
    print(rows)
    assert(len(rows), 1)
    
    existed_urls = rows[0][3]

    query = '''DELETE FROM viktor_files WHERE username=%s AND filename=%s'''
    cur.execute(query, [username, filename])
    conn.commit()
    
    query = '''INSERT INTO viktor_files(username, filename, urls) VALUES(%s, %s, %s)'''
    cur.execute(query, [username, filename, json.dumps(existed_urls + [f"{host}:{port}"]) ])
    conn.commit()
    
    cur.close()

'''
POST Request
Returns: host and port of data_server that's ready to receive file to write,
         or error: 'FILE EXIST' if file exists,
         or reason: done if file written in psql
WARNING: be sure that's server that receive host and port of data_server
         would immediately start uploading file to data_server

Parameters: encoded username, token, filename(optionaly), data_host(optionally), data_port(optionaly),reason
    reason: "upload" - receive data_server
            "done" - say controller file have been sent to data_server 
                     then controller save data_server's url to database
    data_host and data_port: send these when reason = "done", these are host and port of data_server
    filename: send that when reason = "done"
'''
@app.route('/get_disk', methods=['POST'])
def handleDiskRequest():
    if request.method == 'POST':
        if RequestUploadData.is_valid_data(request.files) \
            and LoginData.is_valid_data(request.files):
            cur = conn.cursor()
            username = request.files['username'].stream.read().decode()
            filename = request.files['filename'].stream.read().decode()

            query = "SELECT * FROM viktor_files WHERE username=%s AND filename=%s"
            cur.execute(query, [username, filename])
            rows = list(cur.fetchall())
            print(rows)
            cur.close()
            if len(rows) == 1:
                return {
                    'error': 'FILE EXIST'
                }

            reason = request.files['reason'].stream.read().decode()
            if reason == 'upload':
                r_host, r_port = choice(DATA_SERVERS)
                return {
                    'error': 'None',
                    'data_host': f'{r_host}',
                    'data_port': f'{r_port}'
                }
            
            elif reason == 'done' \
                and RequestUploadData.is_exist_filename_and_url(request.files):
                
                cur = conn.cursor()
                host = request.files['data_host'].stream.read().decode()
                port = request.files['data_port'].stream.read().decode()
                urls = json.dumps([f"{host}:{port}"])

                query = '''INSERT INTO viktor_files(username, filename, urls) VALUES(%s, %s, %s)'''
                cur.execute(query, [username, filename, urls])
                conn.commit()
                cur.close()
    
                # send request to copy_center to start copying data
                data_to_send = {
                    'data_host': host.encode(),
                    'data_port': port.encode(),
                    'username': username.encode(),
                    'filename': filename.encode(),
                    'token': controller_token.encode()
                }
                reqs.post('http://172.20.10.2:10050/copy_start',
                          files=data_to_send)

                return {
                    'reason': 'done'
                }
                
            else:
                print('WRONG', request.files)
                return 'WRONG PARAMETERS'
                

        else:
            print('WRONG', request.files)
            return 'WRONG PARAMETERS'
    else:
        return 'ITS FILE CTRLLER ROUTE! NO GET'

class LoginData:
    def __init__(self) -> None:
        pass

    @staticmethod
    def is_valid_data(data: dict) -> bool:
        return \
        'username' in data.keys() \
        and 'token' in data.keys()
                
class RequestUploadData:
    def __init__(self) -> None:
        pass

    @staticmethod
    def is_exist_filename_and_url(data: dict) -> bool:
        return \
        'filename' in data.keys() \
        and 'data_host' in data.keys() \
        and 'data_port' in data.keys()

    @staticmethod
    def is_valid_data(data: dict) -> bool:
        return \
        'reason' in data.keys()


if __name__ == '__main__':
    app.run(host='172.20.10.2', port=10000, debug=True)