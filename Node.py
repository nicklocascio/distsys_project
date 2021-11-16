#!/usr/bin/bash python3

import sys
import json
import socket

class Node():
    def __init__(self, host, port, self_port):
        self.self_port = self_port
        try:
            self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.sock.bind(('0.0.0.0', self.self_port))
            self.peers = self.connect(host, port)['PEERS']  
        except:
            self.sock = -1

    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

    def get_peers(self):
        pass

    def listen(self):
        while True:
            bytesAddressPair = self.sock.recvfrom(1024)

            message = bytesAddressPair[0]

            address = bytesAddressPair[1]

            clientMsg = "Message from Client:{}".format(message)
            clientIP  = "Client IP Address:{}".format(address)
    
            print(clientMsg)
            print(clientIP)

    def broadcast(self):
        msg = 'hello'
        enc_msg = json.JSONEncoder().encode(msg).encode('utf-8')
        for peer in self.peers:
            self.sock.sendto(enc_msg, tuple(peer))




    def connect(self, host, port):
        req = {'method': 'CONNECT', 'HOST': socket.gethostname(), 'PORT': self.self_port}
        print(req)
        enc_req = json.JSONEncoder().encode(req).encode(encoding='utf-8')
        print(enc_req)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((str(host), int(port)))
        except:
            print('error connecting')
            return -1
        
        try:   
            sock.sendall(enc_req)
        except:
            print('error sending')

        try:
            enc_msg = sock.recv(1024)
        except:
            print('error recieving')
        
        msg = json.JSONDecoder().decode(enc_msg.decode('utf-8', 'strict'))

        print(msg)
        return msg




        

