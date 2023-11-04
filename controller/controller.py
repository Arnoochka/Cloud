import socket
import os
import tqdm
import sys

from constants import *
from replication import Replication

class Controller:
    def __init__(self) -> None:
        pass

    @staticmethod
    def loop() -> None:
        try:
            # TCP SOCKET
            s = socket.socket()
            h = socket.socket()
            print('SOCKET[IPV4, TCP] created')
        except socket.error as err:
            print('SOCKET[IPV4, TCP] creation error: ', err)

        s.bind((CTRLLER_HOST, CTRLLER_PORT))

        print(f'[*] LISTENING as {CTRLLER_HOST}:{CTRLLER_PORT}')
        h.connect((DATA_HOST, 10001))
        while True:
            s.listen(1)
            client_socket, address = s.accept()
            print(f'[+] {address} is conntected')

            received = client_socket.recv(BUFFER_SIZE).decode()
            username, filename, filesize = received.split(SEPARATOR)
            # remove absolute path if there is
            filename = os.path.basename(filename)
            filesize = int(filesize)

            
            h.sendall(f'{username}{SEPARATOR}{filename}{SEPARATOR}{filesize}'.encode())
            progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            while True:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:
                    # nothing is received
                    print(f'[!] Got zero data from {address}')
                    progress.update(len(bytes_read))
                    break
                
                h.sendall(bytes_read)
                progress.update(len(bytes_read))
            
            
            continue

            db_userfolder = DATA_FOLDER + username
            if not os.path.exists(db_userfolder):
                os.makedirs(db_userfolder)

            '''
            start receiving the file from the socket
            and writing to the file stream
            '''
            progress = tqdm.tqdm(range(filesize), 
                                f'Receiving {filename}',
                                unit='B', unit_scale=True,
                                unit_divisor=1024)
            with open(db_userfolder + '/' + filename, 'wb') as f:
                while True:
                    # read BUFFER_SIZE[default=4096] bytes from the socket
                    bytes_read = client_socket.recv(BUFFER_SIZE)
                    if not bytes_read:
                        # nothing is received
                        print(f'[!] Got zero data from {address}')
                        break
                    # write to the file the bytes we just received
                    f.write(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))


if __name__ == "__main__":
    Controller.loop()