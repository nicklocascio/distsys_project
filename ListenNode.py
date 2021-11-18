#!/usr/bin/bash python3

import sys
import json
from Node import Node

from _thread import *
import threading

sock_lock = threading.Lock()
peers_lock = threading.Lock()



def threaded(node):
    while True:
        msg, addr = node.listen()
        print('addr: ', addr)
        print('msg: ', msg)
        try:
            if msg['method'] == 'BROADCAST_PEERS':
                with peers_lock:
                    node.peers = msg['PEERS']
        except:
            print('Denied Request: Invalid Msg Format')


def main():
    if len(sys.argv) != 4:
        return -1

    try:
        host = str(sys.argv[1])
    except:
        return -1

    try:
        port = int(sys.argv[2])
    except:
        return -1

    try:
        self_port = int(sys.argv[3])
    except:
        return -1
        
    node = Node(host, port, self_port)

    if node.sock == -1:
        print('Failed to connect to socket')
        return -1
    elif node.peers == None:
        print('Failed to get peers')
        return -1
        
    reciever = threading.Thread(target=threaded, args=(node,))
    reciever.start()
    

if __name__ == '__main__':
	main()
