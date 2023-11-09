import time
import requests

def start_client(filepath: str):
        data = {'login': 'viktor'.encode(),
                'token': '9313607170&'.encode(),
                'filename': 'yourFatMother.png'.encode(),
                'end': 'true'.encode()}
        
        t = time.time()
        with open(filepath, 'rb') as f:
                chunk = f.read(1024 * 1024)
                data['file_chunk'] = chunk
                response = requests.post(
                        'http://172.20.10.2:10000/upload_to_ctrller', 
                        files=data)
                print(response)

start_client('/Users/maus/Documents/GitHub/Cloud/server/image.jpg')