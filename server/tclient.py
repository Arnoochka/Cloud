import requests
import os
import sys

data = {'login': 'motherfucker-at-your-house',
        'password': 'inside-your-dad'}

response = requests.post('http://localhost:8888/login', json=data)

print(response)

data = {'Authorization': response.content.decode(),
        'files':['']
    }
response = requests.post('http://localhost:8888/get_file', json=data)

if response.status_code == 200:
    print('it is seemed to be done')
else:
    print(response.status_code, response.content.decode())


