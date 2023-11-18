from flask import Flask
from flask import request
from flask import abort
import multiprocessing as mp
import os
import sys
import requests as reqs

app = Flask(__name__)

host_port: str = ''

data_server_token = 'DS_TOKEN' # storing here is unsafe


'''
GET Request
Uses only for connection between data servers and copy_center
It says that data server must immediately to send chunks

Starts sending post requests with username, filename, file_chunk to sender

Parameters: encoded destination_data_server's host and ' port, username, filename
'''
@app.route('/get_data', methods=['GET'])
def handleCopyCenterRequest():
    if request.method != 'GET':
        return {
            'error': 'Bad Request'
        }
    
    # asure requests is correct
    request_keys = request.files.keys()
    print(request_keys)
    if not ('host' in request_keys and 'port' in request_keys):
        return {
            'error': 'Bad Request'
        }
    
    ds_host = request.files['host'].stream.read().decode()
    ds_port = request.files['port'].stream.read().decode()
    username = request.files['username'].stream.read()
    filename = request.files['filename'].stream.read()

    data_to_send = {
        'filename': filename,
        'username': username,
        'token': data_server_token.encode(),
        'end': 'false'.encode()
    }
    with open(f'/Users/maus/Documents/GitHub/Cloud/{host_port}/{username.decode()}/[END]{filename.decode()}', 'rb') as f:
        chunk = f.read(1024 * 1024)
        data_to_send['file_chunk'] = chunk
        if not chunk:
            data_to_send['end'] = 'true'.encode()

        reqs.post(f'http://{ds_host}:{ds_port}/upload_to_data_server', 
                files=data_to_send)
        
    return {
        'error': 'None'
    }

'''
GET Request
Uses to make this data server send request to another data server
    in order to start receiving data from second

Parameters: encoded token, destination_data_server's host and port, username, filename
'''
@app.route('/start_receiving_data_from_another_ds', methods=['GET'])
def handleDataServerRequest():
    if request.method != 'GET':
        return {
            'error': 'Bad Request'
        }
    
    # asure requests is correct
    request_keys = request.files.keys()
    print(request_keys)
    if not ('host' in request_keys and 'port' in request_keys):
        return {
            'error': 'Bad Request'
        }
    
    ds_host = request.files['host'].stream.read().decode()
    ds_port = request.files['port'].stream.read().decode()
    username = request.files['username'].stream.read()
    filename = request.files['filename'].stream.read()

    data_to_send = {
        'filename': filename,
        'username': username,
        'token': data_server_token.encode(),
        'host': host_port[:host_port.find(':')].encode(),
        'port': host_port[host_port.find(':') + 1:].encode()
    }
    
    reqs.get(f'http://{ds_host}:{ds_port}/get_data',
             files=data_to_send)
    
    return {
        'error': 'None'
    }

def upload_file(dir: str, filename: str, chunk: bytes, end: str) -> int:
    filepath = f'/Users/maus/Documents/GitHub/Cloud/{host_port}/{dir}'
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    if os.path.exists(f'/Users/maus/Documents/GitHub/Cloud/{host_port}/{dir}/[END]{filename}'):
        return -1

    with open(f'{filepath}/{filename}', '+ba') as f:
        f.write(chunk)

    if end == 'true':
        os.rename(f'{filepath}/{filename}', 
                  f'/Users/maus/Documents/GitHub/Cloud/{host_port}/{dir}/[END]{filename}')
        return 0
    

    return 1


@app.route('/upload_to_data_server', methods=['POST'])
def handleFile():
    if request.method == 'POST':
        if UploadData.is_valid_data(request.files) \
            and LoginData.is_valid_data(request.files):

            if upload_file(request.files['username'].stream.read().decode(),
                        request.files['filename'].stream.read().decode(),
                        request.files['file_chunk'].stream.read(),
                        request.files['end'].stream.read().decode()) == -1:
                return abort(400)
            

            return 'Hello, World!'
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
                

class UploadData:
    def __init__(self) -> None:
        pass

    @staticmethod
    def is_valid_data(file: dict) -> bool:
        return 'file_chunk' in file.keys() \
        and 'filename' in file.keys() \
        and 'end' in file.keys()
    

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('WRONG ARGUMENTS: USE: HOST PORT')
    else:
        host_port = f'{sys.argv[1]}:{sys.argv[2]}'
        app.run(host=sys.argv[1], port=int(sys.argv[2]), debug=True)