import os
import asyncio
from aiohttp import web
import aioconsole
import asyncpg
import multiprocessing as mp
import time
    
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
    
    def copy(self, queue: mp.Queue):
        copy_Queue = mp.Queue()
        while not queue.empty():
            data = queue.get()

            copy_Queue.put(data)
        return copy_Queue
    
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
            print(queue.get()) #отправка, что можно забирать
        time.sleep(1)
        
async def is_valid(user_token):
    return user_token == "he45stogddf8g70sd7g0g7sd07gs05"