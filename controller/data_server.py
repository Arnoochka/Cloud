from flask import Flask
from flask import request
from flask import abort
import os
import sys

app = Flask(__name__)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('WRONG ARGUMENTS: USE: HOST PORT')
    else:
        app.run(host=sys.argv[1], port=int(sys.argv[2]))