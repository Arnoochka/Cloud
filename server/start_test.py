import os
from multiprocessing import Process
import time
import requests

def client(number):
    data = {'login': f'admin_{str(number)}',
            'password': 'inside-your-dad'}

    t = time.time()
    response = requests.post('http://localhost:8080/login', json=data)
    
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