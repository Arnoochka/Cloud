import os
from multiprocessing import Process
import time
import requests
from config import *

def loop_send_file(url: str='http://192.168.34.210:48901',login: str='victor', token: str=USER_TOKEN, filename: str='victor_world', path: str='/Users/maus/Desktop/victor_world'):
        response = requests.get(url+'/start', files={'token': token.encode(), 'login': login.encode()})

        if 'sorry' not in response.json():
                with open(path, 'rb') as file:
                        i = 1
                        data = {
                                'login': login.encode(),
                                'token': token.encode(),
                                'chunk': ''.encode(),
                                'name': filename.encode(),
                                'end': 'false'.encode()
                        }
                        while True:
                                f = file.read(1024*1024*3)
                                if not f:
                                        data['chunk'] = ''.encode()
                                        data['end'] = 'true'.encode()
                                        response = requests.post(url+'/upload', files=data)
                                        break

                                data['chunk'] = f
                                response = requests.post(url+'/upload', files=data).json()

                                if 'sorry' in response: break

                                i += 1

def client(number):
    data = {'login': f'admin_{str(number)}',
            'password': 'inside-your-dad'}

    t = time.time()
    response = requests.post(f"http://{IP_VICTOR}:8011/authorization", json=data)
    
    if not (response.status_code >= 200 and response.status_code < 300):
        print(f"Process_{number}: pizda")
        return
    data = {
        'token': response.content.decode(),
        'login': f'admin_{str(number)}',
        'filename': "hello.txt"
    }
    
    response = requests.post(f'http://{IP_VICTOR}:8011/send_file', json=data)
    
    if not (response.status_code >= 200 and response.status_code < 300):
        print(f"Process_{number}: blya, {response.status_code}")
        return
    
    print(f"Process_{number}: начинается процесс отправки")
    
    loop_send_file(login=data['login'], url=response.content.decode(), filename=data['filename'], path="C:\home screen\programming\Cloud\Cloud\server\hello.txt")
        
    print(time.time() - t)


if __name__ == "__main__":
    n = int(input())
    answers = [0]*n
    Processes = [Process]*n
    p = Process(target=client, args=(0, ))
    p.start()
    p.join()
    for i in range(n):
        Processes[i] = Process(target=client, args=(i + 1, ))
        Processes[i].start()
    for i in range(n):
        Processes[i].join()