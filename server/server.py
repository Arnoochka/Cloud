import asyncio
from aiohttp import web
import aiomysql
import multiprocessing


async def handle_post_request(request):
    data = await request.post()
    
    # Получаем картинку из данных запроса
    image = data['file']
    image_data = image.file.read()
    
    # Сохраняем картинку на сервере
    with open(f"{data['name']}", 'wb') as f:
        f.write(image_data)
    
    # Возвращаем ответ клиенту
    return web.Response(200)

class input_server:
    def __init__(self, host, port) -> None:
        self.app = web.Application()
        self.app.router.add_post('/', handle_post_request)
        self.runner = web.AppRunner(self.app)
        self.site = web.TCPSite(self.runner, host, port)
        self.users = dict()
        self.users_on_server = dict()
        self.users_cloud = dict()
        
    async def start_server(self):
        
        await self.runner.setup()
        await self.site.start()
        
        
    async def connect(self, request):
        data = await request.post()
        pass
    async def using():
        pass

class output_server(self, host, port):
    def __init__(self, host, port):
        pass
    
    
loop = asyncio.get_event_loop()
loop.run_until_complete(input_server('localhost', 8888).connect())
loop.run_forever()