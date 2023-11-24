from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

def run_ftp_server():
    # Создание объекта-авторизатора
    authorizer = DummyAuthorizer()
    authorizer.add_user("username", "password", ".", perm="elradfmw")

    # Настройка обработчика FTP-сессии
    handler = FTPHandler
    handler.authorizer = authorizer

    # Запуск FTP-сервера на порту 21
    server = FTPServer(("0.0.0.0", 21), handler)
    
    print("FTP сервер запущен. Подключитесь с помощью FTP-клиента.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Сервер остановлен.")

if __name__ == "__main__":
    run_ftp_server()
