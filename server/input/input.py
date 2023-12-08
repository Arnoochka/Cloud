import os
import asyncio
from aiohttp import web, ClientSession
import aioconsole
import asyncpg
import multiprocessing as mp
import aioconsole
import io
import sys
from config import *
 
class Input:
    def __init__(self, host: str, port: int, main_database_url: dict, main_database_credentials: dict):
        self.host = host
        self.port = port
        self.app = web.Application(middlewares=[self.mid])
        
        self.main_database = (main_database_url, main_database_credentials)
        
        self.databases = [self.main_database]

        self.app.router.add_post('/authorization', self.autorization)
        self.app.router.add_post('/add_helper', self.add_helper)
    
    async def mid(self, app, handler):
        '''
        '''
        async def middleware(request: web.Request) -> web.Response:
            
            data = await request.json()
            
            if request.path == "/authorization":
                if len(self.databases) == 0:
                    return web.Response(status=500)
                
                not_atribute = await self.checking_for_attributes(["login", "password"], data.keys())
                
                if not_atribute[0]:
                    return web.Response(status=401, body=f"not received {not_atribute[1]}")
                
                return await handler(data)
            
            elif data['token'] == SERVER_TOKEN:
                if request.path == "/add_helper":
                    not_atribute = await self.checking_for_attributes(["URL", "credentials"], data.keys())
                
                if not_atribute[0]:
                    return web.Response(status=401, body=f"not received {not_atribute[1]}")
                        
                return await handler(data)
            
            return web.Response(status=404)
        
        return middleware 
    
    async def start_server(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        await aioconsole.aprint(f"сервер Input, {self.port}, {self.host}")

    async def autorization(self, data: dict)->web.Response:

        not_atribute = await self.checking_for_attributes(["login", "password"], data.keys())
        if not_atribute[0]:
            return web.Response(status=401, body=f"not received {not_atribute[1]}")
        
        async with ClientSession() as session:
            try:
                data['token'] = SERVER_TOKEN
                async with session.post(url=f"{self.main_database[0]}/authorization", json=data, timeout=4) as response:
                    if response.status == 200 or response.status == 201:
                        return web.Response(status=response.status, body=USER_TOKEN)
                    else:
                        return web.Response(status=response.status)
            except :
                if len(self.databases) == 1:
                    self.databases.pop(0)
                    return web.Response(status=500)
                
                else:
                    data_main = {
                        'token': SERVER_TOKEN,
                        'databases': dict()
                    }
                    
                    for i in range(2, len(self.databases)):
                        data_main['databases'][self.databases[i][0]] = self.databases[i][1]
                        
                    await self.new_main(data_main)
                    

    async def add_helper(self, data: dict):
        self.databases.append((data["URL"], data["credentials"]))
        async with ClientSession() as session:
            try:
                response = await session.post(url=f"{self.main_database[0]}/add_helper", json=data, timeout=5)
                return web.Response(status=200)
            except :
                self.databases.pop(-1)
                return web.Response(status=404)
                
    
    async def new_main(self, data_main: dict):
        self.databases.pop(0)
        self.main_database = self.databases[0]
        async with ClientSession() as session:
            try:
                async with session.post(url=f"{self.main_database[0]}/switch_role", json=data_main, timeout=5) as response:
                    delete = list()
                    for i in range(1, len(self.databases)):
                        try:
                            response = await session.post(url=f"{self.databases[i][0]}/new_main", json={"token": SERVER_TOKEN, "URL": self.main_database[0], "credentials": self.main_database[1]})
                        except :
                            delete.append(i)
                            
                    shift = 0
                    for x in delete:
                        self.databases.pop(x - shift)
                        shift += 1
                                
                
            except :
                await self.new_main(data_main)
                
    async def send_file(self, data: dict)->web.Response:
        pass
    
    async def get_files(self, data: dict)->web.Response:
        pass
        
    async def checking_for_attributes(self, atributes: list, data_atribute)->tuple:
        for atribute in atributes:
            if not atribute in data_atribute:
                return (1, atribute)
        return (0, "not")
    
    def __repr__(self) -> str:
        return f"URL=http://{self.host}:{self.port}, main database={self.main_database[0]}, number_databases = {len(self.databases)}"

async def main(port=8888):
    credentials = {
        "user": "admin",
        "password": "root",
        "database": "admin",
        "host": IP_VICTOR
    }
    
    input_server = Input(IP_VICTOR, port, f"http://{IP_VICTOR}:8000", credentials)
    await input_server.start_server()
    
    command = ''
    while True:
        command = await aioconsole.ainput()
        if command == "/stop":
            break
        elif command == "/settings":
            print(input_server)

if __name__ == "__main__":
    asyncio.run(main())
    
    