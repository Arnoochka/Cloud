from ftplib import FTP

def run_ftp_client():
    # Подключение к локальному FTP-серверу
    ftp = FTP('localhost')
    ftp.login(user='username', passwd='password')

    file_name = "1.txt"

    # Отправка файла на сервер
    with open(f'client/{file_name}', 'rb') as file:
        ftp.storbinary(f'STOR {file_name}', file)

    print("Файл успешно отправлен на сервер.")

    file_name = "2.txt"

    # Получение файла с сервера
    with open(f'client/{file_name}', 'wb') as file:
        ftp.retrbinary(f'RETR {file_name}', file.write)

    print("Файл успешно получен с сервера.")

    # Закрытие соединения
    ftp.quit()

if __name__ == "__main__":
    run_ftp_client()
