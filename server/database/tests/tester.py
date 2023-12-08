import requests
import sys
from config import *

credentials = {
        "user": "admin",
        "password": "root",
        "database": "admin",
        "host": IP_VICTOR
    }

if __name__ == "__main__":
    response = requests.post(f"http://{IP_TIMUR}:8001/new_main", json={"token": DATABASE_TOKEN, "URL": f"http://{IP_VICTOR}:8000", "credentials": credentials})
    print(response.status_code)
    
    response = requests.post(f"http://{IP_VICTOR}:8002/new_main", json={"token": DATABASE_TOKEN, "URL": F"http://{IP_VICTOR}:8000", "credentials": credentials})
    print(response.status_code)
    
    credentials_1 = {
        "user": "admin",
        "password": "root",
        "database": "admin",
        "host": IP_TIMUR
    }
    
    credentials_2 = {
        "user": "admin",
        "password": "root",
        "database": "postgres",
        "host": IP_VICTOR
    }
    
    data = {"token": "cf1e8c14e54505f60aa10ceb8d5d8ab3", 
            "databases":{f"http://{IP_TIMUR}:8001": credentials,
                        f"http://{IP_VICTOR}:8002": credentials
        }
    }
    response = requests.post(url=f"http://{IP_VICTOR}:8000/switch_role", json=data)
    print(response.status_code)
    
    data = {
        'token': SERVER_TOKEN,
        'URL':f"http://{IP_TIMUR}:8001",
        "credentials": credentials_1
    }
    response = requests.post(url=F"http://{IP_VICTOR}:8888/add_helper", json=data)
    print(response.status_code)
    
    data = {
        'token': SERVER_TOKEN,
        'URL':f"http://{IP_VICTOR}:8002",
        "credentials": credentials_2
    }
    response = requests.post(url=f"http://{IP_VICTOR}:8888/add_helper", json=data)
    print(response.status_code)
    
    for i in range(100):
        data = {"login": f"admin_{i}", "password": "root"}
        response = requests.post(url=f"http://{IP_VICTOR}:8888/authorization", json=data)
        print(f"admin_{i}", response.status_code)