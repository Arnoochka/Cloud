import socket
import os
import tqdm

from constants import DATA_HOST, BUFFER_SIZE, SEPARATOR, DATA1_FOLDER
from replication import Replication

import sys

class DataServer:
    def __init__(self) -> None:
        pass

    @staticmethod
    def loop(port: int, data_folder: str) -> None:
        try:
            # TCP SOCKET
            s = socket.socket()
            print('SOCKET[IPV4, TCP] created')
        except socket.error as err:
            print('SOCKET[IPV4, TCP] creation error: ', err)

        s.bind((DATA_HOST, port))

        print(f'[*] LISTENING as {DATA_HOST}:{port}')
        while True:
            s.listen(1)
            client_socket, address = s.accept()
            print(f'[+] {address} is conntected')

            received = client_socket.recv(BUFFER_SIZE).decode()
            username, filename, filesize = received.split(SEPARATOR)
            # remove absolute path if there is
            filename = os.path.basename(filename)
            filesize = int(filesize)

            db_userfolder = data_folder + '/' + username
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
                        progress.update(len(bytes_read))
                        break
                    # write to the file the bytes we just received
                    f.write(bytes_read)
                    # update the progress bar
                    progress.update(len(bytes_read))
            
    
if __name__ == '__main__':
    DataServer.loop(10001, DATA1_FOLDER)