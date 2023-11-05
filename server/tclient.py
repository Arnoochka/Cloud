import requests
import os
import sys
import time
import asyncio
import aiohttp
import io
from base64 import b64decode as dec64
from base64 import b64encode as enc64

async def client(number):
    data = {'login': f'admin_{str(number)}',
            'password': 'inside-your-dad'}

    t = time.time()
    response = requests.post('http://localhost:8080/login', json=data)
    response.content
    
    data = {
            'login': f"admin_{number}",
            'files': [], 
            'files_names': "image.jpg",
            'token': response.content
    }
    with io.open("Cloud/server/image.jpg", "rb") as file:
        new_file = ["start".encode()]
        while True:
                f = file.read(1024)
                if not f:
                        new_file.append("end".encode())
                        break
                new_file.append(f)
                
        data = {
            'login': f"admin_{number}",
            'file_chunk': [], 
            'file_name': "image.jpg",
            'token': response.content.decode()
        }        
        async with aiohttp.ClientSession() as session:
                for chunk in new_file:
                        data['file_chunk'] = chunk
                        response = await session.post("http://localhost:8888/send_file", data = data)
                        print(response.status)
                    
                    
    
if __name__=="__main__":
        asyncio.run(client(1000))



