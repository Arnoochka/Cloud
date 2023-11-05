import os
import socket

from constants import COPY_HOST, COPY_PORT, COPY_SEPARATOR, BUFFER_SIZE

try:
    # TCP SOCKET
    s = socket.socket()
    print('SOCKET[IPV4, TCP] created')
except socket.error as err:
    print('SOCKET[IPV4, TCP] creation error: ', err)

s.bind((COPY_HOST, COPY_PORT))
print(f'[*] LISTENING as {COPY_HOST}:{COPY_PORT}')
while True:
    s.listen(1)
    client_socket, addr = s.accept()
    print(f'[+] {addr} connected')

    received = client_socket.recv(BUFFER_SIZE).decode()
    
