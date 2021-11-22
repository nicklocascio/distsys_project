import pickle
import socket
import sys
import threading
import time
import queue
import random

'''
How I think this system needs to work after comments and class discussion

#### Networking nuances ####
- Bind one socket to port for listening for transactions
- Use HTTP requests for name server
- Use another socket to send to (address, port) pairs on block broadcast
- USE PORTS 9000-10000 

1) Miner registers itself with name server
2) Create a thread to repeatedly check in with name server while alive,
as well as pulling other peers from name server (HTTP Request)
3) Create a thread to listen for incoming transactions
4) Add transactions to a block until full, then begin mining process
5) If a valid hash is found, broadcast that block to all other miners
6) If a hashed block is received, add it to your chain
7) Need to figure out how to declare one chain the victor when 
multiple chains develop under competition

- We need to have some third party client that is sending transactions
to the miners
1) Should repeatedly pull miners from name server and send transactions to them
'''

def name_server():
    # need to come up with catalog format


    return

def listener():

    return

def main():
    # create socket for listening to register with name server
    listen_port = random.randint(9000, 10000)
    ip_addr = socket.gethostbyname(socket.gethostname())
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.bind(('0.0.0.0', listen_port))

    # create name server thread
    name_server_thread = threading.Thread(target=name_server, daemon=True, args=([listen_port, ip_addr]))
    name_server_thread.start()

    # create listening thread
    listener_thread = threading.Thread(target=listener, daemon=True, args=([listen_sock]))
    listener_thread.start()

    # main program loop to pull transactions from queue and work on mining

    return

if __name__ == "__main__":
    main()