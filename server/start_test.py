import os
from multiprocessing import Process
import time
import requests
import io

def client(number):
    data = {'login': f'admin_{str(number)}',
            'password': 'inside-your-dad'}

    t = time.time()
    response = requests.post('http://localhost:8080/login', json=data)
    
    data = {
            'login': f"admin_{number}",
            'files': [], 
            'files_names': "image.jpg",
            'token': response.content
    }

    new_file = ["start".encode()]
    with io.open("Cloud/server/image.jpg", "rb") as file:
        new_file = ["start".encode()]
        while True:
                f = file.read(1024 * 1024)
                if not f:
                        new_file.append("end".encode())
                        break
                new_file.append(f)
    data = {
        'login': f"admin_{number}",
        'file_name': "image.jpg",
        'token': response.content.decode()
    }        
    for chunk in new_file:
        response = requests.post('http://localhost:8888/send_file', files={"file_chunk": chunk}, data=data)
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