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
import json
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
ip_list = ["192.168.34.5:8011", "192.168.34.5:8012", "192.168.34.5:8013", "192.168.34.5:8014"]
ip = ""
files = []
del_fil = []


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
                response = requests.post(f'http://{ipp}/authorization', json=data, timeout=5)
            except:
                pass
            else:
                if response.status_code == 200:
                    token = response.content.decode()  
                    ip = ipp            
                    break
        
        print(token)

class FileViewScreen(BoxLayout):
    def on_enter(self):
        super().on_enter()
        self.update_file_list()

    def update_file_list(self):
        global ip_list
        global files
        global login
        global token
        global del_fil
        

        for ipp in ip_list:
            try:
                response = requests.get(f"http://{ipp}/get_files_names", json={"login": login, "token": token})
            except:
                pass
            else:
                if response.status_code == 200:        
                    break

        #response = requests.get(f"http://{ip_list[0]}/get_files_names", json={"login": login, "token": token})
        print(response.status_code)
        #rs = '{"FILENAMES": ["1.txt", "2.txt", "3.png"]}'
        json_data = json.loads(response.content.decode())
        files = json_data["FILENAMES"]

        files = [i for i in files if i not in del_fil]


        recycle_view = self.ids.file_view_rv

        recycle_view.data = []

        for name in files:
            file_name = name
            recycle_view.data.append({'file_name': file_name, 'delete_button': 'Delete', 'download_button': 'Download'})


    def delete_file(self, instance):
        print(instance)
        del_fil.append(instance)


    def download_file(self, instance):
        global ip_list
        global files
        global login
        global token

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
        filename = instance

        for ipp in ip_list:
            try:
                response = requests.post(f'http://{ipp}/get_file', json={'login': login, 'filename': filename, 'token': token})
            except:
                pass
            else:
                if response.status_code == 200:        
                      break
            
        #response = requests.post(f'http://{ip_list[0]}/get_file', json={'login': login, 'filename': filename, 'token': token})
        url = response.content.decode()

        print(response.status_code)
        print(url, "===")

        response = requests.get(url + '/download', json={
        'login': login,
        'filename': filename,
        'token': token
        })

        file_stream = response.content
        with open(filename, 'wb') as file_object:
            file_object.write(file_stream)

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
        global ip_list
        global del_fil

        file_path:str = value[0]
        file_name = file_path.split("\\")[-1]
        
        if file_name in del_fil:
            del_fil.remove(file_name)

        data = {
        'token': token,
        'login': login,
        'filename': file_name
        }

        print(data)

        for ipp in ip_list:
            try:
                response = requests.post(f'http://{ipp}/send_file', json=data)
            except:
                pass
            else:
                if response.status_code == 200:        
                    break


        #response = requests.post(f'http://{ip_list[0]}/send_file', json=data)
        if response.status_code != 401:
            url = response.content.decode()
            print(response.status_code)
            response = requests.get(url+'/start', files={'token': token.encode(), 'login': login.encode()})
            print("db code=", response.status_code)

            if 'sorry' not in response.json():
                    with open(file_path, 'rb') as file:
                            i = 1
                            data = {
                                    'login': login.encode(),
                                    'token': token.encode(),
                                    'chunk': ''.encode(),
                                    'name': file_name.encode(),
                                    'end': 'false'.encode()
                            }
                            while True:
                                    f = file.read(1024*1024*3)
                                    if not f:
                                            data['chunk'] = ''.encode()
                                            data['end'] = 'true'.encode()
                                            response = requests.post(url+'/upload', files=data)
                                            break

                                    data['chunk'] = f
                                    response = requests.post(url+'/upload', files=data).json()

                                    if 'sorry' in response: break

                                    i += 1

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
        token = data['token']
        login = data['login']


        response = requests.get(url+'/start', files={'token': token, 'login': login})
        print("db code=", response.status_code)

        if 'sorry' not in response.json():
            pass

        for chunk in new_file:
            response = requests.post(f"http://{url}/send_file", data=data, files={"file_chunk": chunk})
            files[response.content.decode()] = file_name
            print(response.content)
            print(files)



if __name__ == '__main__':
    KeyValueApp().run()