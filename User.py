import pickle
import socket
import sys
import threading
import time
import queue
import random
import json
import requests

def main():
    # create socket for listening to register with name server
    listen_port = random.randint(9000, 10000)
    ip_addr = socket.gethostbyname(socket.gethostname())
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.connect(('student06.cse.nd.edu', 9554))
    listen_sock.sendall('hello'.encode('utf-8'))

if __name__ == "__main__":
    main()