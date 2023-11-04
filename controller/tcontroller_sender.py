import socket
import os
import tqdm

CTRLLER_HOST = '0.0.0.0'
CTRLLER_PORT = 9990

BUFFER_SIZE = 4096
SEPARATOR = '<SEP>'

filename = '/Users/maus/g.cpp'
filesize = os.path.getsize(filename)

s = socket.socket()

print(f'[+] Connecting to {CTRLLER_HOST}:{CTRLLER_PORT}')
s.connect((CTRLLER_HOST, CTRLLER_PORT))
print('[+] Connected')

s.send(f'igor{SEPARATOR}{filename}{SEPARATOR}{filesize}'.encode())

# start sending the file
progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
with open(filename, "rb") as f:
    while True:
        # read the bytes from the file
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            # file transmitting is done
            break
        # we use sendall to assure transimission in 
        # busy networks
        s.sendall(bytes_read)
        # update the progress bar
        progress.update(len(bytes_read))
# close the socket
s.close()

