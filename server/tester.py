import requests

DATABASE_TOKEN = "11e0eed8d3696c0a632f822df385ab3c"
SERVER_TOKEN = "cf1e8c14e54505f60aa10ceb8d5d8ab3"

credentials = {
        "user": "admin",
        "password": "root",
        "database": "admin",
        "host": "127.0.0.1"
    }

if __name__ == "__main__":
    response = requests.post("http://localhost:8001/new_main", json={"token": DATABASE_TOKEN, "URL": "http://localhost:8000", "credentials": credentials})
    print(response.status_code)
    response = requests.post("http://localhost:8002/new_main", json={"token": DATABASE_TOKEN, "URL": "http://localhost:8000", "credentials": credentials})
    print(response.status_code)
    data = {"token": "cf1e8c14e54505f60aa10ceb8d5d8ab3", 
            "databases":{"http://localhost:8001": credentials,
                        "http://localhost:8002": credentials
        }
    }
    response = requests.post(url="http://localhost:8000/switch_role", json=data)
    print(response.status_code)
    data = {"token": SERVER_TOKEN, "login": "admin", "password": "root"}
    response = requests.post(url="http://localhost:8000/authorization", json=data)
    print(response.status_code)