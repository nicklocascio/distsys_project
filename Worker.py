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
from Block import Block

from User import broadcast


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

NOTES ON TRANSACTIONS FOR WHEN WE ADD VERIFICATION
- how to ensure that a user starts with some sort of balance?
- are we actually going to parse through entire blockchain for every transaction?
  seems like this will work on our scale but in reality is not very scalable

'''

def broadcast(broadcast_queue):
    while True:
        # Get peers and broadcast a message
        if broadcast_queue.qsize() > 0:
            peers = broadcast_queue.get()
            broadcast_queue.task_done()
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as u:
                u.bind(('0.0.0.0', 0))
                for peer in peers:
                    u.connect(peer)
                    u.sendall('whats up my fellow workers'.encode('utf-8'))

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
                    if address['project'] == 'hash_worker' and address["lastheardfrom"] + 20 > time.time():
                        peers.append((address['name'], address['port']))

            peers_queue.put(peers)

        time.sleep(10)

def listener(listen_sock, transaction_queue):
    while True:
        msg = listen_sock.recv(1024)
        msg = msg.decode('utf-8', 'strict')
        # include a check for if msg is a block opposed to a transaction

        
        transaction_queue.put(msg)

def main():
    # create socket for listening to register with name server
    listen_port = random.randint(9000, 10000)
    ip_addr = socket.gethostbyname(socket.gethostname())
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.bind(('0.0.0.0', listen_port))

    # Queues for resource sharing
    peers_queue = Queue()
    transaction_queue = Queue()
    broadcast_queue = Queue()

    # Create name server thread
    name_server_thread = threading.Thread(target=name_server, daemon=True, args=([listen_port, ip_addr, peers_queue]))
    name_server_thread.start()

    # Create listening thread
    listener_thread = threading.Thread(target=listener, daemon=True, args=([listen_sock, transaction_queue]))
    listener_thread.start()

    # Initialize blockchain list
    blockchain = []
    curr_block = Block.genesis_block()

    # Main program loop to pull transactions from queue and work on mining
    while True:

        if peers_queue.qsize() > 0:
            peers_list = peers_queue.get()
            print(peers_list)
            peers_queue.task_done()
            broadcast_queue.put(peers_list)
            broadcast(broadcast_queue)
        
        if transaction_queue.qsize() > 0:
            msg = transaction_queue.get()
            print(msg)
            transaction_queue.task_done()

            # this message is what we will insert into block and also can add the verification step here
            # Might need some logic to parse transaction - similar to client logic

            # Verify transaction before inserting into block - this might work
            # this wouldn't include sending to other users, but rather just 
            # adding and subtracting money, which does illustrate the general concept
            txn_ledger = {}
            for block in blockchain:
                for transaction in block.transactions:
                    amount = transaction["Amount"]
                    if amount < 0:
                        try:
                            new_amount = txn_ledger[transaction["User"]] - amount
                            if new_amount < 0:
                                # throw out transaction, results in negative balance
                                continue
                            else:
                                txn_ledger[transaction["User"]] = new_amount
                        except Exception:
                            continue
                    else:
                        try:
                            txn_ledger[transaction["User"]] += amount
                        except Exception:
                            txn_ledger[transaction["User"]] = amount


            # Insert verified transaction into block and check if we need to mine
            status = curr_block.add_transaction(msg)
            if status == "Full":
                Block.mine(curr_block)
                # broadcast block to other peers
                blockchain.append(curr_block)
                prev_block = curr_block
                curr_block = Block.new_block(prev_block)

if __name__ == "__main__":
    main()