#!/bin/bash/python3
# -*- coding: utf-8 -*-
from flask import Flask
from flask_sockets import Sockets
import os

app = Flask(__name__)
sockets = Sockets(app)

@sockets.route('/echo')
def echo_socket(ws, *args, **kwargs):
    message = ws.receive()
    print('msg recv:', message)
    ws.send(message)

if __name__ == '__main__':
    socketio.run(app, debug=True)
