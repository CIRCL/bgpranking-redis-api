#!/usr/bin/env python

import zmq

ip = '127.0.0.1'
port = '5556'

zmq_socket = None


def __prepare():
    global zmq_socket
    context = zmq.Context()
    zmq_socket = context.socket(zmq.SUB)
    zmq_socket.connect('tcp://{}:{}'.format(ip, port))
    zmq_socket.setsockopt(zmq.SUBSCRIBE, '')

def run():
    if zmq_socket is None:
        __prepare()
    while True:
        msg = zmq_socket.recv()
        yield msg

if __name__ == '__main__':
    for a in run():
        print a

