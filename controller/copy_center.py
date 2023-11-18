from flask import Flask
from flask import request
from flask import abort
import multiprocessing as mp
from constants import DATA_SERVERS
import requests as reqs
from random import choice

app = Flask(__name__)

copy_center_token = 'CC_TOKEN' # storing here is unsafe


'''
POST Request
Returns:

Parameters: encoded username, filename, data_server host-post, controller_token
'''
@app.route('/copy_start', methods=['POST'])
def handleControllerRequest():
    if request.method != 'POST':
        return {
            'error': 'Undefinded'
        }
    
    # asure request is correct
    request_keys = request.files.keys()
    print(request_keys)
    if not ('token' in request_keys \
        and 'username' in request_keys \
        and 'filename' in request_keys \
        and 'data_host' in request_keys \
        and 'data_port' in request_keys):
        
        return {
            'error': 'Bad Request'
        }  
    
    token = request.files['token'].stream.read()
    filename = request.files['filename'].stream.read()
    username = request.files['username'].stream.read()
    host = request.files['data_host'].stream.read()
    port = request.files['data_port'].stream.read()

    data_to_send = {
        'filename': filename, 
        'username': username,
        'host': host,
        'port': port,
        'token': copy_center_token
    }

    r_host,r_port = choice(DATA_SERVERS)
    while r_host != host.decode() and str(r_port) != port.decode():
        r_host, r_port = choice(DATA_SERVERS)

    reqs.get(f'http://{r_host}:{r_port}/start_receiving_data_from_another_ds',
                files=data_to_send)
    return {
        'error': 'None'
    }



if __name__ == '__main__':
    app.run(host='172.20.10.2', port=10050, debug=True)