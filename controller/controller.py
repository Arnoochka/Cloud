from flask import Flask
from flask import request
from flask import abort
import os
import multiprocessing as mp

app = Flask(__name__)

def upload_file(dir: str, filename: str, chunk: bytes, end: str) -> int:
    filepath = f'/Users/maus/Documents/GitHub/Cloud/data/{dir}'
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    if os.path.exists(f'/Users/maus/Documents/GitHub/Cloud/data/{dir}/[END]{filename}'):
        return -1

    with open(f'{filepath}/{filename}', '+ba') as f:
        f.write(chunk)

    if end == 'true':
        os.rename(f'{filepath}/{filename}', 
                  f'/Users/maus/Documents/GitHub/Cloud/data/{dir}/[END]{filename}')
        return 0
    

    return 1


@app.route('/upload_to_ctrller', methods=['POST'])
def handleFile():
    if request.method == 'POST':
        if UploadData.is_valid_data(request.files) \
            and LoginData.is_valid_data(request.files):

            if upload_file(request.files['login'].stream.read().decode(),
                        request.files['filename'].stream.read().decode(),
                        request.files['file_chunk'].stream.read(),
                        request.files['end'].stream.read().decode()) == -1:
                return abort(400)
            

            return 'Hello, World!'
        else:
            print('WRONG', request.files)
            return 'WRONG PARAMETERS'
    else:
        return 'ITS FILE CTRLLER ROUTE! NO GET '
    
class LoginData:
    def __init__(self) -> None:
        pass

    @staticmethod
    def is_valid_data(data: dict) -> bool:
        return \
        'login' in data.keys() \
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
    app.run(host='172.20.10.2', port=10000)