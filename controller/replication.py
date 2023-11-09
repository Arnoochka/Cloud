import threading
import multiprocessing
import os

from constants import *

class Replication:
    def __init__(self) -> None:
        pass

    @staticmethod
    def copy_file(username: str, filename: str) -> None:
        '''
        Copy file into user's folder in REPL_FOLDER
        '''

        bpdb_filepath = REPL_FOLDER + username
        if not os.path.exists(bpdb_filepath):
            os.makedirs(bpdb_filepath)

        bpdb_filepath += '/' + filename
        db_filepath = DATA_FOLDER + username + '/' + filename

        os.system(f'cp "{db_filepath}" "{bpdb_filepath}"')

    @staticmethod
    def copy_all(source: str, dest: str, username: str) -> None:
        '''
        Copy data from user's folder in DATA_FOLDER into user's folder in REPL_FOLDER
        '''
        os.system(f'rm -rf {dest}/{username}')
        os.system(f'cp -r "{source}/{username}" "{dest}"')
