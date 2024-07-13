import time
import requests

def start_client(filepath: str):
        data = {'username': 'viktor'.encode(),
                'token': '21249953&'.encode(),
                'filename': 'Surrounder.png'.encode(),
                'reason': 'upload'.encode(),
                'end': 'true'.encode()}
        
        t = time.time()
        with open(filepath, 'rb') as f:
                chunk = f.read(1024 * 1024)
                data['file_chunk'] = chunk
                response = requests.post(
                        'http://172.20.10.2:10000/get_disk', 
                        files=data)
                response = response.json()
                requests.post(
                        f'http://{response["data_host"]}:{response["data_port"]}/upload_to_data_server', 
                        files=data)
                
        
        data['reason'] = 'done'.encode()
        data['data_host'] = f'{response["data_host"]}'.encode()
        data['data_port'] = f'{response["data_port"]}'.encode()
        response= requests.post(
                'http://172.20.10.2:10000/get_disk',
                files=data
        )
        print(response.json())



start_client('/Users/maus/Documents/GitHub/Cloud/server/image.jpg')