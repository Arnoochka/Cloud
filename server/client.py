import os
import aiohttp
import asyncio
import aioconsole
import queue

class client:
    def __init__(self) -> None:
        self.login = "admin"
        self.password = "password"
        self.host = "127.0.0.1"
        self.port = 8888
        url = 'http://localhost:8888'
        self.tasks = queue.Queue()
        
        
async def start_client(self):
    
    while True:
        if await self.autorization():
            command = aioconsole.ainput()
            if command == "/send": 
                await self.send_command(command)
                await self.send_file()
            else:
                print("неизвестная команда")
        else:
            return
             
async def autorization(self)->bool:
    async with aiohttp.ClientSession() as session:
        async with session.post(self.url, data = {'login': self.login, 'password':self.password}) as response:
            return int(await response.text()) == 200
                
async def send_command(self, command):
    async with aiohttp.ClientSession() as session:
        data = {"command": command}
        async with session.post(self.url, json = data) as response:
            code = int(await response.text())
            if code == 200:
                print("команда успешно отправлена")
            else:
                print("ошибка")
    
async def send_file(self):
    await self.send_command("/send file")
    with open('file directory', 'rb') as file:
        data = {'file':file.read(), 'name': 'file_name', 'login': self.login}
        
    async with aiohttp.ClientSession() as session:
        async with session.post(self.url, data = data) as response:
            code = int(await response.text())
            if code == 200:
                print("файл успешно отправлен")
            else:
                print("ошибка")


if __name__=="__main__":    
    
    asyncio.run(client().start_client())