
import requests

chunk = "0000000000".encode()

data = {
                'login': "1",
                #'file_chunk': ["0000000000".encode()],
                'filename': "0.txt",
                'token': "he45stogddf8g70sd7g0g7sd07gs05"
            }

response =  requests.post("http://192.168.154.5:8000/send_file", data=data, files={"file_chunk": chunk})
print(response.content)