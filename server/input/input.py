import os
import asyncio
from aiohttp import web, ClientSession
import aioconsole
import asyncpg
import multiprocessing as mp
import aioconsole
import io
DATABASE_TOKEN = "11e0eed8d3696c0a632f822df385ab3c"
SERVER_TOKEN = "cf1e8c14e54505f60aa10ceb8d5d8ab3"
USER_TOKEN = "ee11cbb19052e40b07aac0ca060c23ee"
DB_TOKEN = "d77d5e503ad1439f585ac494268b351b"
CONTROLLER_TOKEN = "594c103f2c6e04c3d8ab059f031e0c1a"
    
class Input:
    def __init__(self, host: str, port: int):
        self.host = host
        
        self.port = port
        self.app = web.Application(middlewares=[self.mid])
        
        self.app['db'] = None
        self.insert_sql = '''INSERT INTO registered(login, password) VALUES($1, $2)'''
        self.select_sql = '''SELECT * FROM registered WHERE login=$1'''
        self.search_files_sql = '''SELECT filename FROM userFile WHERE login=$1'''

        self.app.router.add_post('/authorization', self.autorization)
    
    async def mid(self, app, handler):
        '''
        '''
        async def middleware(request: web.Request) -> web.Response:
            
            data = request.json()
            
            if request.path == "/aгthorization":
                return await handler(request)
            
            return web.Response(status=404)
        
        return middleware 
    
    async def start_server(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        await aioconsole.aprint(f"сервер input_server, {self.port}, {self.host}")

    async def autorization(self, data: dict)->web.Response:

        not_atribute = await self.checking_for_attributes(["login", "password"], data.keys())
        if not_atribute[0]:
            return web.Response(status=401, body=f"not received {not_atribute[1]}")
        
        person = await self.app['db'].fetch(self.select_sql, data["login"])
        if len(person) == 0:
            await self.app['db'].fetch(self.insert_sql, data["login"], data["password"])
            return web.Response(status=201, body=self.bearer_token)
        elif person[0]["password"] == data["password"]:
            return web.Response(status=200, body= self.bearer_token)
        else: 
            return web.Response(status=401, body= "invalid login or password")

    async def checking_for_attributes(self, atributes: list, data_atribute)->tuple:
        for atribute in atributes:
            if not atribute in data_atribute:
                return (1, atribute)
        return (0, "not")
    