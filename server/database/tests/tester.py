import requests

DATABASE_TOKEN = "11e0eed8d3696c0a632f822df385ab3c"
SERVER_TOKEN = "cf1e8c14e54505f60aa10ceb8d5d8ab3"

credentials = {
        "user": "admin",
        "password": "root",
        "database": "admin",
        "host": "172.20.10.2"
    }

if __name__ == "__main__":
    response = requests.post("http://172.20.10.3:8001/new_main", json={"token": DATABASE_TOKEN, "URL": "http://172.20.10.2:8000", "credentials": credentials})
    print(response.status_code)
    
    credentials = {
        "user": "admin",
        "password": "root",
        "database": "admin",
        "host": "172.20.10.2"
    }
    
    response = requests.post("http://172.20.10.2:8002/new_main", json={"token": DATABASE_TOKEN, "URL": "http://172.20.10.2:8000", "credentials": credentials})
    print(response.status_code)
    
    credentials_1 = {
        "user": "admin",
        "password": "root",
        "database": "admin",
        "host": "172.20.10.3"
    }
    
    credentials_2 = {
        "user": "admin",
        "password": "root",
        "database": "postgres",
        "host": "172.20.10.2"
    }
    
    data = {"token": "cf1e8c14e54505f60aa10ceb8d5d8ab3", 
            "databases":{"http://172.20.10.3:8001": credentials,
                        "http://172.20.10.2:8002": credentials
        }
    }
    response = requests.post(url="http://172.20.10.2:8000/switch_role", json=data)
    # print(response.status_code)
    for i in range(100):
        data = {"token": SERVER_TOKEN, "login": f"admin_{i}", "password": "root"}
        response = requests.post(url="http://172.20.10.2:8000/authorization", json=data)
        print(response.status_code)