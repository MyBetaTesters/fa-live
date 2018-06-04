#!/bin/bash/python3
# -*- coding: utf-8 -*-
import os
import logging
import redis
import gevent
import json
from flask import Flask
from flask_sockets import Sockets

REDIS_URL = os.environ['REDIS_URL']
REDIS_CHAN = 'adsb'

app = Flask(__name__)
sockets = Sockets(app)
redis = redis.from_url(REDIS_URL, decode_responses=True)

class AdsbReceiver(object):
    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            app.logger.info(u'Sending message: {}'.format(data))
            yield data
            print(data)

    def register(self, client):
        self.clients.append(client)

    def send(self, client, data):
        message = json.loads(data)
        if hasattr(client, 'callsign') and 'callsign' in message:
            if message['callsign'] == client.callsign:
                return
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        gevent.spawn(self.run)

recvr = AdsbReceiver()
recvr.start()

@sockets.route('/chat')
def inbox(ws):
    # append callsign to websocket, if included in first comunication
    message = json.loads(ws.receive())
    if 'callsign' in message:
        ws.callsign = message['callsign']

    app.logger.info(u'connected: {}'.format(message))
    redis.publish(REDIS_CHAN, message)
    recvr.register(ws)

    # continue looping for new messages
    while not ws.closed:
        # Sleep to prevent *constant* context-switches.
        gevent.sleep(0.1)
        data = ws.receive()

        if data:
            app.logger.info(u'message: {}'.format(data))
            redis.publish(REDIS_CHAN, message)

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
