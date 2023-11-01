from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivy.uix.filechooser import FileChooserListView
import requests

Builder.load_file('main.kv')

class KeyValueApp(MDApp):
    def build(self):
        return MainScreen()

class MainScreen(BoxLayout):
    pass   

class KeyValueScreen(BoxLayout):
    def send_request(self):
        # Receive user' key and value 
        key = self.ids.key_input.text
        value = self.ids.value_input.text

        # Dictionary key-value
        data = {key: value}

        response = requests.post('https://localhost:8888', json=data)

        if response.status_code == 200:
            print("[KV]Request sent successfully")
            print("Answer from server: ", response.text)
        else:
            print("Request post error")

class FileUploadScreen(BoxLayout):
    def open_file_chooser(self):
        self.file_chooser = FileChooserListView()
        self.file_chooser.bind(on_submit=self.upload_file)
        self.add_widget(self.file_chooser)

    def upload_file(self, instance, value, h):
        file_path:str = value[0]
        files = {'file': open(file_path, 'rb').read()}

        response = requests.post('http://localhost:8888', 
                                 files=files, 
                                 data={'name': "later_add_name_blyat"})

        if response.status_code == 200:
            print("[FILE]Request sent successfully")
            print("Answer from server: ", response.text)
        else:
            print("Request post error")

if __name__ == '__main__':
    KeyValueApp().run()