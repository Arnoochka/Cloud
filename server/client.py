import os
import aiohttp
import asyncio
import aioconsole

class client:
    def __init__(self) -> None:
        self.login = "admin"
        self.password = "password"
        self.host = "127.0.0.1"
        self.port = 8888
        self.url = 'http://localhost:8888'
        
        self.token= ''
        
        
    async def start_client(self):
        if await self.autorization():
            while True:
                    command = await aioconsole.ainput()
                    if command == "/send": 
                        await self.send_file()
                    else:
                        print("неизвестная команда")
             
    async def autorization(self)->bool:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.url}/login" , json = {'login': self.login, 'password':self.password}) as response:
                 self.token = await response.text()
                 return response.status == 200
                 

    async def send_command(self, command):
        async with aiohttp.ClientSession() as session:
            data = {"command": command}
            async with session.post(f"{self.url}/send_file", json = data) as response:
                code = await response.text()
                if int(code) == 200:
                    print("команда успешно отправлена")
                else:
                    print("ошибка")

    async def send_file(self):
        with open('image.jpg', 'rb') as file:
            data = {'file':file.read(), 'filename': 'file_name.jpg', 'token': self.token}
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.url}/send_file", data = data) as response:
                answer = await response.text()
                if answer == 200:
                    print("файл успешно отправлен")
                else:
                    print(response.status, answer)


if __name__=="__main__":    
    my_client = client()
    asyncio.run(my_client.start_client())