#!/bin/bash/python3
# -*- coding: utf-8 -*-
from flask import Flask
from flask_socketio import SocketIO
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret!')
socketio = SocketIO(app)

@socketio.on('message')
def handle_message(message):
    emit('new message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
