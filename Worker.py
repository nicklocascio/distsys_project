import pickle
import socket
import sys
import threading
import time
import queue
import random
import json
import requests
from queue import Queue


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

def name_server(listen_port, ip_addr, peers_queue):
    # need to come up with catalog format
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as u:
            
            # Register for Catalog
            u.bind(('0.0.0.0', 0))
            u.connect(('catalog.cse.nd.edu', 9097))
            ns_msg = {
                'type' : 'hashtable',
                'owner' : 'jbigej',
                'port' : listen_port,
                'address' : ip_addr,
                'project' : 'hash_worker'
            }

            u.sendall(json.JSONEncoder().encode(ns_msg).encode(encoding='utf-8'))

            print('registered')

            # Get peers from the catalog
            r = requests.get('http://catalog.cse.nd.edu:9097/query.json')
            address_book = json.JSONDecoder().decode(r.text)
            peers = []

            for address in address_book:
                if 'project' in address:
                    if address['project'] == 'hash_worker':
                        peers.append((address['name'], address['port']))

            peers_queue.put(peers)

        time.sleep(10)

def listener(listen_sock, transaction_queue):
    while True:
        msg = listen_sock.recv(1024)
        msg = msg.decode('utf-8', 'strict')
        transaction_queue.put(msg)

def main():
    # create socket for listening to register with name server
    listen_port = random.randint(9000, 10000)
    ip_addr = socket.gethostbyname(socket.gethostname())
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.bind(('0.0.0.0', listen_port))
    peers_queue = Queue()
    transaction_queue = Queue()

    # Create name server thread
    name_server_thread = threading.Thread(target=name_server, daemon=True, args=([listen_port, ip_addr, peers_queue]))
    name_server_thread.start()

    # Create listening thread
    listener_thread = threading.Thread(target=listener, daemon=True, args=([listen_sock, transaction_queue]))
    listener_thread.start()

    # Main program loop to pull transactions from queue and work on mining
    while True:

        if peers_queue.qsize() > 0:
            msg = peers_queue.get()
            print(msg)
            peers_queue.task_done()
        
        if transaction_queue.qsize() > 0:
            msg = transaction_queue.get()
            print(msg)
            transaction_queue.task_done()

if __name__ == "__main__":
    main()