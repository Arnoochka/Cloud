import os
import asyncio
from aiohttp import web, ClientSession
import aioconsole
import asyncpg
import multiprocessing as mp
import time
import aioconsole
import io

host = 'localhost'
    
class input_server:
    def __init__(self, host: str, port: int):
        self.host = host
        
        self.port = port
        self.app = web.Application(middlewares=[self.mid])
        
        self.app['db'] = None
        self.insert_sql = '''INSERT INTO registered(login, password) VALUES($1, $2)'''
        self.select_sql = '''SELECT * FROM registered WHERE login=$1'''
        self.search_files_sql = '''SELECT nameFile FROM userFile WHERE login=$1'''

        self.app.router.add_post('/login', self.autorization)
        self.app.router.add_post('/send_file', self.send_file)
        self.app.router.add_get("/name_files", self.get_file_name)
        self.app.router.add_post("/get_file", self.get_file)
        
        self.transport_servers_URL = []
        
        self.bearer_token = "he45stogddf8g70sd7g0g7sd07gs05"
        
        self.url_controller = ""
    
    async def mid(self, app, handler):
        '''
        '''
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
        if len(person) == 0:
            await self.app['db'].fetch(self.insert_sql, data["login"], data["password"])
            return web.Response(status=201, body=self.bearer_token)
        elif person[0]["password"] == data["password"]:
            return web.Response(status=200, body= self.bearer_token)
        else:
            return web.Response(status=401, body= "invalid login or password")

    
    async def send_file(self, request: web.Request)->web.Response:
        
        data = await request.post()
         # логика
        #...
        
        not_atribute = await self.checking_for_attributes(['token', 'file', 'filename'], data.keys())
        if not_atribute[0]:
            return web.Response(status=401, body=f"not received {not_atribute[1]}")
        
        return web.Response(status=200, body="URL транспортного сервера")

            
    async def get_file_name(self, request: web.Request):
        
        login = await request.query.get('login')
        
        person = await self.app['db'].fetch(self.search_files_sql, login)
        
        return web.json_response(person)
        
    async def get_file(self, request: web.Request):
        
        data = await request.post()
        # логика
        #...
        return web.Response(status=200, body="URL транспортного сервера")
        
            
    async def checking_for_attributes(self, atributes: list, data_atribute)->tuple:
        for atribute in atributes:
            if not atribute in data_atribute:
                return (1, atribute)
        return (0, "not")
              
class transport_server:
    def __init__(self, host: str, port: int, MAX_PROCESS: int, MAX_SIZE_Q):
        
        self.host = host
        self.port = port
        self.app = web.Application()
    
        self.app.router.add_post('/send_file', self.send_file)
        self.app.router.add_post("/get_file", self.get_file) 
        
        self.bearer_token = "he45stogddf8g70sd7g0g7sd07gs05"
        self.number_process = 0
        
        self.using_send_queue = mp.Queue()
        self.MAX_SIZE_Q = MAX_SIZE_Q
        self.send_task_done = mp.Queue()
        
        self.job_process = [mp.Process(target=demon_write_file, args=(self.using_send_queue, self.send_task_done)) for i in range(MAX_PROCESS)]
        self.process_task_done = mp.Process(target=demon_send_done_task, args=(self.send_task_done, ))
        
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
        
        for i in range(len(self.job_process)):
            self.job_process[i].daemon = True
            self.job_process[i].start()
            
        self.process_task_done.daemon = True
        self.process_task_done.start()
        
        
    async def send_file(self, request: web.Request):
        
        data = await request.post()
        
        not_atribute = await self.checking_for_attributes(["login", 'file_chunk', 'file_name', 'token'], data.keys())
        if not_atribute[0]:
            return web.Response(status=401, body=f"not received {not_atribute[1]}")
        
        chunk = data["file_chunk"].file.read()
        
        self.using_send_queue.put({"login": data["login"], "file_chunk": chunk, "file_name": data["file_name"]})
        
        return web.Response(status= 200, body="OK")
    
    async def get_file(self, request: web.Request):
        pass
    
    async def checking_for_attributes(self, atributes: list, data_atribute: set)->tuple:
        for atribute in atributes:
            if not atribute in data_atribute:
                return (1, atribute)
        return (0, "not")
    
    def stop_process(self):
        for i in range(len(self.job_process)):
            self.job_process[i].terminate()
        self.process_task_done.terminate()
    
    
def demon_write_file(queue: mp.Queue, queue_done: mp.Queue):
    while True:
        if not queue.empty():
            data = queue.get()
            chunk_file = data['file_chunk']
            if chunk_file == 'start'.encode():
                if not os.path.isdir(f"files/{data['login']}"):
                    os.mkdir(f"files/{data['login']}")
                file = open(f"files/{data['login']}/{data['file_name']}", "w")
                file.close()
                continue
            
            if chunk_file == 'end'.encode():
                queue_done.put((data['login'], data['file_name']))    
            
            
            with open(f"files/{data['login']}/{data['file_name']}", "+ba") as file:
                file.write(chunk_file)

def demon_send_done_task(queue: mp.Queue):
    while True:
        if not queue.empty():
            senf_file_to_controller(queue.get())
        time.sleep(.1)
        
async def senf_file_to_controller(data):
    with io.open("files/admin_0/monologue.mp4", "rb") as file:
        new_file = []
        data['end'] = 'false'.encode()
        while True:
                f = file.read(1024 * 1024)
                if not f:
                        new_file.append('end'.encode())
                        break
        
                new_file.append(f)  
                     
        async with ClientSession() as session:
                for chunk in new_file:
                        data['file_chunk'] = chunk
                        if chunk == 'end'.encode():
                            data['file_chunk']=b''
                            data['end'] = 'true'.encode()
                        response = await session.post("http://172.20.10.2:10000/upload_to_ctrller", data = data)
                        print(response.status)
        
async def is_valid(user_token):
    return user_token == "he45stogddf8g70sd7g0g7sd07gs05"
    

async def start_server_async_run(host, port, number, queue: mp.Queue):
    my_transport_server = transport_server(host, port, number, 50)
    await my_transport_server.start_server()
    while queue.empty(): 
        await asyncio.sleep(.1)
    my_transport_server.stop_process()

def start_transport_server(host, port, number, queue: mp.Queue):
    asyncio.run(start_server_async_run(host, port, number, queue))
    
async def main():           
    my_input_servers = input_server(host, 8080)
    
    number_transport_servers = 3
    number_demon_process = 3
        
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
    ]
    transport_servers = []
    terminate_queue = mp.Queue()
    for i in range(number_transport_servers):
        my_input_servers.transport_servers_URL.append(f"http://localhost:{ 8000 + i}")
        transport_servers.append(mp.Process(target = start_transport_server, args = (host, 8000 + i, number_demon_process, terminate_queue)))
        transport_servers[i].start()
        
    await asyncio.gather(*tasks)
    
    command = ''
    while command != "/stop":
        command = await aioconsole.ainput()
        if command == "/stop":
            terminate_queue.put(command)
            
            num_ended_process = 0
            while num_ended_process != len(transport_servers):
                for process in transport_servers:
                    if not process.is_alive():
                        num_ended_process += 1
    
if __name__ == "__main__":
    asyncio.run(senf_file_to_controller({'login': 'admin_0'.encode(), 'filename': 'monologue.mp4'.encode(), 'token': "he45stogddf8g70sd7g0g7sd07gs05".encode()}))