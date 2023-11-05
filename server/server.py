import os
import asyncio
from aiohttp import web
from aiohttp import ClientSession
import aioconsole
import asyncpg
from multiprocessing import Process
    
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
        self.app.router.add_post("/name_files", self.get_file_name)
        self.app.router.add_post("/get_file", self.get_file)
        
        self.transport_server = []
        
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
        
        await aioconsole.aprint(f"сервер input_server c портом {self.port}")
        
        

    async def autorization(self, request: web.Request)->web.Response:
        data = await request.json()
        
        not_atribute = await self.checking_for_attributes(["login", "password"], data.keys())
        if not_atribute[0]:
            return web.Response(status=401, body=f"not received {not_atribute[1]}")
        
        person = await self.app['db'].fetch(self.select_sql, data["login"])
        print(data['login'])
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
        
        return web.Response(status=200, body="http://localhost:8888/send_file")

        # отправка данных контроллеру
        
        async with ClientSession() as session:
            async with session.post(f"{self.url_controller}/send_file", data = data) as response:
                return await response
            
    async def get_file_name(self, request: web.Request):
        
        data = await request.post()
        
        return web.Response(status=200, body="http://localhost:8888/get_file_name")
        
        #получение имен файлов от сервера
        async with ClientSession() as session:
            async with session.get(f"{self.url_controller}/get_file_name", params = data) as response:
                return await response
    
    async def get_file(self, request: web.Request):
        
        data = await request.post()
        
        return web.Response(status=200, body="http://localhost:8888/get_files")
        
        async with ClientSession() as session:
            async with session.get(f"{self.url_controller}/get_file", data = request['data']) as response:
                return await response
        
            
    async def checking_for_attributes(self, atributes: list, data_atribute)->tuple:
        for atribute in atributes:
            if not atribute in data_atribute:
                return (1, atribute)
        return (0, "not")
              
class transport_server:
    def __init__(self, host, port):
        
        self.host = host
        self.port = port
        self.app = web.Application()
        
        self.app['db'] = None
        self.insert_sql = '''INSERT INTO registered(login, password) VALUES($1, $2)'''
        self.select_sql = '''SELECT * FROM registered WHERE login=$1'''
    
        self.app.router.add_post('/send_file', self.send_file)
        self.app.router.add_post("/name_files", self.get_file_name)
        self.app.router.add_post("/get_file", self.get_file) 
        
        self.bearer_token = "he45stogddf8g70sd7g0g7sd07gs05"
        self.number_directory = 0
        
    async def mid(self, app, handler):
        async def middleware(request: web.Request) -> web.Response:
            
            response = web.Response(status=401, body="invallid token")
            
            if request.headers.get("token"):
                if is_valid(request.content['token']):
                    response = handler(request)
            
            return response
        
        return middleware 
        
    async def start_server(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        await aioconsole.aprint(f"сервер transport_server c портом {self.port}")
        
    async def send_file(self, request: web.Request):
        
        data = await request.post()
        
        not_atribute = await self.checking_for_attributes(["login", 'file_chunk', 'file_name', 'token'], data.keys())
        if not_atribute[0]:
            return web.Response(status=401, body=f"not received {not_atribute[1]}")
        
        chunk_file = data['file_chunk'].file.read()
        
        if chunk_file == 'start'.encode():
            if not os.path.isdir(f"files/{data['login']}"):
                os.mkdir(f"files/{data['login']}")
                
            file = open(f"files/{data['login']}/{data['file_name']}", "+wb")
            file.close()
            return web.Response(status=200, body="start writing")
        
        if chunk_file == 'end'.encode:
            os.rename(f"files/{data['login']}/{data['file_name']}.bin", f"files/{data['login']}/{data['file_name']}.{data['file_name']}")
            return web.Response(status=200, body="file has written")
        
        with open(f"files/{data['login']}/{data['file_name']}", "+ba") as file:
            file.write(chunk_file)
            return web.Response(status=200, body="chuck saved")
    
    async def get_file_name():
        pass
    
    async def get_file():
        pass
    
    async def checking_for_attributes(self, atributes: list, data_atribute: set)->tuple:
        for atribute in atributes:
            if not atribute in data_atribute:
                return (1, atribute)
        return (0, "not")
    
    
async def main():
    my_input_servers = input_server('localhost', 8080)
    my_transpot_servers = transport_server('localhost', 8888)
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
        print("Connection to databes successfuly")
    pool.acquire()
    my_input_servers.app['db'] = pool
    tasks = [
        asyncio.create_task(my_input_servers.start_server()),
        asyncio.create_task(my_transpot_servers.start_server())
    ]
    await asyncio.gather(*tasks)
    
    while True:
        command = await aioconsole.ainput()
        if command == "/stop":
            break
    
if __name__ == "__main__":
    asyncio.run(main())