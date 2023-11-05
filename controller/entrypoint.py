from controller import Controller
from replication import Replication

import tqdm
import os
import socket
from constants import *

from threading import Thread
from queue import Queue

class ReplicationWorker(Thread):
    def __init__(self, username: str):
        Thread.__init__(self)
        self.username = username

    def run(self):
        Replication.copy_all(self.username)
        


def entrypoint():
    import time
    usernames = ['egor','igor','ivan','nikolay','suka ebannaya', 'timur', 'viktor']

    start = time.time()
    workers =[]
    for username in usernames:
        worker = ReplicationWorker(username)
        workers.append(worker)
        worker.start()

    print(time.time() - start)
    while 1:
        pass



if __name__ == '__main__':
    entrypoint()