import asyncio
from aiohttp import web, ClientSession
import asyncio
import aioconsole
import asyncpg
import multiprocessing as mp
import aioconsole
import sys
import json
from config import *

SELECT_SQL = '''SELECT * FROM registered WHERE login=$1'''
INSERT_SQL = '''INSERT INTO registered(login, password) VALUES($1, $2)'''

class MainDatabase:
    
    def __init__(self) -> None:
        self.helper_url = list()
        self.helper_database = list()
        self.number_helper = 0
        self.index_next = -1
    
    async def send_helper(self, data: dict) -> web.Response:
        async with ClientSession() as session:
            try:
                async with session.post(url=f"{self.helper_url[self.index_next]}/send_database", json=data, timeout=5) as response:
                    print(f"{self.helper_url[self.index_next]}/send_database")
                    return web.Response(status=response.status)
                    
            except :
                self.helper_database.pop(self.index_next)
                self.helper_url.pop(self.index_next)
                return web.Response(status=501)
                
    async def get_person(self, data: dict, main_database) -> web.Response:
        
        person_main = await main_database.fetch(SELECT_SQL, data["login"])
        
        try:
            if len(person_main) == 0:
                self.index_next = (self.index_next + 1) % len(self.helper_url)
                person_helper = await self.helper_database[self.index_next].fetch(SELECT_SQL, data["login"], timeout=5)

                if len(person_main) + len(person_helper) == 0: return await self.send_helper(data)
                else:
                    await main_database.fetch(INSERT_SQL, data["login"], data["password"])
                    
        except : 
            self.helper_database.pop(self.index_next)
            self.helper_url.pop(self.index_next)
            return web.Response(status=501)
            
        return web.Response(status=200)
    
    async def add_helper(self, helper_url, helper_database) -> web.Response:
        self.helper_url.append(helper_url)
        self.helper_database.append(helper_database)
        return web.Response(status=201)
    
    def __repr__(self) -> str:
        return f"role=Main, number helper={self.number_helper}"

class HelperDatabase:
    
    def __init__(self) -> None:
        self.main_url = None
        self.main_database = None
    
    async def send_databases(self, data: dict, helper_database) -> web.Response:
        
        await helper_database.fetch(INSERT_SQL, data["login"], data["password"])
        await self.main_database.fetch(INSERT_SQL, data["login"], data["password"])
        
        return web.Response(status=201, body=USER_TOKEN)
    
    def __repr__(self) -> str:
        return f"role=Helper, main url={self.main_url}"
    
class DatabaseServer:
    def __init__(self, host: str, port: str, database_settings: dict) -> None:
        
        self.host = host
        self.port = port
        self.app = web.Application(middlewares=[self.mid])
        self.database_settings = database_settings
        self.app['db'] = None
        self.role = HelperDatabase()
        
        self.is_main = False
        
        self.app.router.add_post('/add_helper', self.add_helper)
        self.app.router.add_post('/new_main', self.new_main)
        self.app.router.add_post("/authorization", self.authorizations)
        self.app.router.add_post("/switch_role", self.switch_role)
        self.app.router.add_post("/send_database", self.send_database)

    async def mid(self, app, handler) -> web.Response:
        '''
        '''
        async def middleware(request: web.Request) -> web.Response:
            data = await request.json()
            if data['token'] == SERVER_TOKEN:
                return await handler(data)
            
            elif data['token'] == DATABASE_TOKEN:
                return await handler(data)
            
            return web.Response(status=400)
        
        return middleware
    
    async def start_server(self):
        self.app['db'] = await self.start_db(self.database_settings)
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        await aioconsole.aprint(f"сервер Database, {self.port}, {self.host}")
        
    async def add_helper(self, data: dict) -> web.Response:
        
        await self.role.add_helper(data["URL"], await self.start_db(data["credentials"]))
        return web.Response(status=200)
            
    async def new_main(self, data: dict) -> web.Response:
        if not self.is_main:
            self.role.main_database = await self.start_db(data["credentials"])
            self.role.main_url = data["URL"]
            return web.Response(status=200)
        else:
            return web.Response(status=500)
        
    async def authorizations(self, data: dict):
        if self.is_main:
            return await self.role.get_person(data, self.app['db'])
        else:
            return web.Response(status=401)
            
    async def switch_role(self, data: dict):
        self.role = MainDatabase()
        self.is_main = True
        for URL in data["databases"].keys():
            await self.role.add_helper(URL, await self.start_db(data["databases"][URL]))
            
        self.role.number_helper = len(self.role.helper_url)
        
        return web.Response(status=200)
    
    async def start_db(self, database: str):
        pool = await asyncpg.create_pool(**database)

        if pool._closed:
            print("Connection failed")
        else:
            print("Connection to databes successfuly")
        
        pool.acquire()
        
        return pool
    
    async def send_database(self, data: dict):
        return await self.role.send_databases(data, self.app['db'])
            

async def main(port):
    credentials = {
        "user": "admin",
        "password": "root",
        "database": "postgres",
        "host": IP_VICTOR,
    }
    server = DatabaseServer(IP_VICTOR, port, credentials)
    await server.start_server()
    
    command = ''
    while True:
        command = await aioconsole.ainput()
        if command == "/stop":
            break
        if command == "/status":
            await aioconsole.aprint(type(server.role))
        
        if command == "/settings":
            print(server.role)
    
     
if __name__ == "__main__":
    port = int(input())
    asyncio.run(main(port=port))