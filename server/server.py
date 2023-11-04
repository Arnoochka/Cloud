import os
import asyncio
from aiohttp import web
from aiohttp import ClientSession
import aioconsole
import asyncpg
import json
    
async def is_valid(user_token):
    return user_token == "he45stogddf8g70sd7g0g7sd07gs05"
    
class input_server:
    def __init__(self, host, port):
        self.host = host
        
        self.port = port
        self.app = web.Application(middlewares=[self.mid])
        
        self.app['db'] = None
        self.insert_sql = '''INSERT INTO registered(login, password) VALUES($1, $2)'''
        self.select_sql = '''SELECT * FROM registered WHERE login=$1'''

        self.app.router.add_post('/login', self.autorization)
        self.app.router.add_post('/send_file', self.send_file)
        self.app.router.add_get("/name_files", self.get_file_name)
        self.app.router.add_post("/get_file", self.get_files)
        
        self.bearer_token = "he45stogddf8g70sd7g0g7sd07gs05"
        
        self.url_controller = ""
    
    async def mid(self, app, handler):
        async def middleware(request) -> web.Response:
            
            if request.path == "/login":
                responce = await handler(request)
                return responce
            else:
                data = await request.post()
                
            if 'token' in data.keys():
                if await is_valid(data['token']):
                    responce = await handler(request)
                else:
                    return web.Response(status=401, body="you are not authorized")
            else:
                return web.Response(status=401, body="you are not authorized")
            
            return responce
        
        return middleware 
    
    async def start_server(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        await aioconsole.aprint(f"сервер запущен c портом {self.port}")
        
        

    async def autorization(self, request: web.Request)->web.Response:
        data = await request.json()
        
        not_atribute = await self.checking_for_attributes(["login", "password"], data.keys())
        if not_atribute[0]:
            return web.Response(status=401, body=f"not received {not_atribute[1]}")
        
        await self.app['db'].fetch(self.insert_sql, "admin", "password")
        person = await self.app['db'].fetch(self.select_sql, data["login"])
        
        if len(person) == 0:
            await self.app['db'].fetch(self.insert_sql, data["login"], data["password"])
            return web.Response(status=201, body=self.bearer_token)
        elif person[0]["password"] == data["password"]:
            return web.Response(status=200, body= self.bearer_token)
        else:
            return web.Response(status=401, body= "invalid login or password")

    
    async def send_file(self, request: web.Request)->web.Response:
        
        data = await request.post()
        
        not_atribute = await self.checking_for_attributes(['token', 'file', 'filename'], data.keys())
        if not_atribute[0]:
            return web.Response(status=401, body=f"not received {not_atribute[1]}")

        # отправка данных контроллеру
        
        async with ClientSession() as session:
            async with session.post(f"{self.url_controller}/send_file", data = data) as response:
                return await response
            
    async def get_file_name(self, request: web.Request):
        
        data = await request.post()
        
        not_atribute = await self.checking_for_attributes(['token', 'files'], data.keys())
        if not_atribute[0]:
            return web.Response(status=401, body=f"not received {not_atribute[1]}")
        
        #получение имен файлов от сервера
        async with ClientSession() as session:
            async with session.get(f"{self.url_controller}/get_file_name", params = data) as response:
                return await response
            
    # async def get_files(self, request: web.Request):
        
    #     not_atribute = await self.checking_for_attributes(['login', 'files'], request)
    #     if not_atribute[0]:
    #         return web.Response(status=401, body=f"not received {not_atribute[1]}")
    #     write_file = Process(target = self.get_file, args=(request, )).start()
        
    #     names_get_files = list()
        
    #     read_and_det_files = Process(target=self.get_file, args=(request, names_get_files))
    #     while not read_and_det_files.is_alive():
    #         await asyncio.sleep(0.1)
    #     return web.Response(status=200, body=names_get_files)
        
        
    # async def get_file(self, request: web.Request, names_get_files):
        
    #     ws = web.WebSocketResponse()
    #     await ws.prepare(request)
        
    #     async for msg in ws:
    #         if msg.type == WSMsgType.TEXT:
    #             filenames = msg.data.split(",")  # получение списка имен файлов из сообщения
                
    #         for filename in filenames:
    #             with open(filename, 'rb') as file:
    #                 await ws.send_bytes(file.read())  # отправка содержимого каждого файла обратно клиенту
    
    async def get_files(self, request: web.Request):
        
        data = await request.json()
        
        not_atribute = await self.checking_for_attributes(['token', 'files'], data.keys())
        if not_atribute[0]:
            return web.Response(status=401, body=f"not received {not_atribute[1]}")
        async with ClientSession() as session:
            async with session.post(f"{self.url_controller}/get_file", data = request['data']) as response:
                return await response
        
            
    async def checking_for_attributes(self, atributes: list, data_atribute)->tuple:
        for atribute in atributes:
            if not atribute in data_atribute:
                return (1, atribute)
        return (0, "not")

            

async def main():
    my_input_servers = input_server('localhost', 8888)
    credentials = {
        "user": "admin",
        "password": "root",
        "database": "postgres",
        "host": "127.0.0.1",
    }
    
    pool = await asyncpg.create_pool(**credentials)
        
    if pool._closed:
        print("Connection failed")
    else:
        print("Connection successful")
    pool.acquire()
    my_input_servers.app['db'] = pool
    tasks = [
        asyncio.create_task(my_input_servers.start_server())
    ]
    await asyncio.gather(*tasks)
    
    while True:
        command = await aioconsole.ainput()
        if command == "/stop":
            break
    
if __name__ == "__main__":
    asyncio.run(main())