from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.properties import StringProperty
from kivy.lang import Builder
import requests
import aiohttp
import io
import asyncio


Builder.load_file('main.kv')

class KeyValueApp(MDApp):
    def build(self):
        return MainScreen()

class MainScreen(BoxLayout):
    pass   


login = ""
password = ""
token = ""
ip_list = ["192.168.154.5"]
ip = ""
files = {"link": "1.txt",
         "link1": "2.txt"}


class AuthorizationScreen(BoxLayout):
    def send_request(self):
        global login
        global password
        global token
        global ip_list
        global ip
        login = self.ids.login_input.text
        password = self.ids.password_input.text

        data = {'login': login, 'password': password}
        for ipp in ip_list:
            try:
                response = requests.post(f'http://{ipp}:8080/login', json=data)
            except:
                pass
            else:
                if response.status_code == 200:
                    token = response.content.decode()  
                    ip = ipp            
                    break


class FileViewScreen(BoxLayout):
    def on_enter(self):
        super().on_enter()
        self.update_file_list()

    def update_file_list(self):
        global files
        
        recycle_view = self.ids.file_view_rv

        # Очищаем текущие виджеты
        recycle_view.data = []


        for link in files:
            file_name = files[link]
            recycle_view.data.append({'file_name': file_name, 'delete_button': 'Delete', 'download_button': 'Download', 'link': link})


    def delete_file(self, instance):
        print(instance)


    def download_file(self, instance):
        global files

        path = files[instance]
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(link) as response:
                with open(path, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
        """
        response = requests.post(instance)
        with open(path, 'wb') as file:
            while True:
                chunk =  response.content.read(1024)
                if not chunk:
                    break
                file.write(chunk)


class FileViewRow(BoxLayout):
    file_name = StringProperty()
    delete_button = StringProperty()
    download_button = StringProperty()

class FileUploadScreen(BoxLayout):
    def open_file_chooser(self):
        self.file_chooser = FileChooserListView()
        self.file_chooser.bind(on_submit=self.upload_file)
        self.add_widget(self.file_chooser)

    
    def show_auth_message(self):
        global login
        global token

        self.clear_widgets()  # Очистить текущие виджеты, если есть

        if login == "" or token == "":
            # Если логин или токен пусты, показываем сообщение
            self.add_widget(Label(text='You need to authenticate first.'))

    def upload_file(self, instance, value, h):
        global login
        global token

        file_path:str = value[0]
        file_name = file_path

        with io.open(file_path, "rb") as file:
            new_file = ["start".encode()]
            while True:
                f = file.read(1024)
                if not f:
                    new_file.append("end".encode())
                    break
                new_file.append(f)

            data = {
                'login': login.encode(),
                'file_chunk': [],
                'filename': file_path.encode(),
                'token': token.encode()
            }

            response = requests.post(f"http://{ip}:8080/send_file", data=data)            
            print(response.content.decode())
            url = response.content.decode()

            asyncio.run(self.upload_chunks(new_file, data, url, file_name))

    async def upload_chunks(self, new_file, data, url, file_name):
        global files
        """
        async with aiohttp.ClientSession() as session:
            for chunk in new_file:
                data['file_chunk'] = chunk

                print(f"http://{url}/send_file")

                response = await session.post(f"http://{url}/send_file", data=data)
                #files={"file_chunk": chunk}
                print(response.status)
        
        """
        for chunk in new_file:
            response = requests.post(f"http://{url}/send_file", data=data, files={"file_chunk": chunk})
            files[response.content.decode()] = file_name
            print(response.content)



if __name__ == '__main__':
    KeyValueApp().run()