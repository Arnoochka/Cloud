import os
import asyncio
from aiohttp import web
from aiohttp import ClientSession
import aioconsole
import asyncpg

    
class input_server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.app = web.Application()
        
        self.app['db'] = None
        self.insert_sql = '''INSERT INTO registered(login, password) VALUES($1, $2)'''
        self.select_sql = '''SELECT login FROM registered'''

        self.app.router.add_post('/login', self.autorization)
        self.app.router.add_post('/send_file', self.send_file)
        self.app.router.add_get("/name_files", self.send_file)
        self.app.middlewares.append(self.middleware)
        
        self.bearer_token = "he45stogddf8g70sd7g0g7sd07gs05"
        
        
        
        self.url_controller = ""
        
    async def middleware(self, app, heandler: callable, request: web.Request)->web.Response:
        if request.path == "/login":
            response = await heandler(request)
        elif request.headers.get("Autorization"):
            if self.bearer_token == request["Autorization"]:
                response = await heandler(request)
            else:
                return web.Response(status=401, body="you not autorization")
        else:
            return web.Response(status=401, body="you not autorization")
        
        return response
            
    async def start_server(self):
        await self.app['db'].fetch(self.insert_sql, "admin", "password")
        otvet = await self.app['db'].fetch(self.insert_sql, "admin", "password")
        print(otvet)
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
        await aioconsole.aprint(f"сервер запущен c портом {self.port}")
        
        

    async def autorization(self, request: web.Request)->web.Response:
        
        if not request.headers.get('login') or not request.headers.get('password'):
            return web.Response(status=400, body="no login or password entered")
        
        data = await request.post()
        
        
        
        print(data['login'], data['password'])
        
        return web.Response(status=200, body="autorization successfully")
    
    async def send_file(self, request: web.Request)->web.Response:
        
        not_atribute = await self.checking_for_attributes(['login', 'file', 'filename'], request)
        if not_atribute[0]:
            return web.Response(status=401, body=f"not received {not_atribute[1]}")
            
        data = await request.post()

        # отправка данных контроллеру
        
        async with ClientSession() as session:
            async with session.post(f"{self.url_controller}/send_file", data = data) as response:
                return await response
            
    async def get_file_name(self, request: web.Request):
        
        not_atribute = await self.checking_for_attributes(['login', 'files'], request)
        if not_atribute[0]:
            return web.Response(status=401, body=f"not received {not_atribute[1]}")
        
        data = await request.get()
        
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
        
        not_atribute = await self.checking_for_attributes(['login', 'files'], request)
        if not_atribute[0]:
            return web.Response(status=401, body=f"not received {not_atribute[1]}")
        async with ClientSession() as session:
            async with session.post(f"{self.url_controller}/get_file_name", data = request['data']) as response:
                return await response
        
            
    async def checking_for_attributes(self, atrubutes: list, request: web.Request)->tuple:
        for atribute in list:
            if not request.headers.get(atribute):
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