import pickle
import socket
import sys
import threading
import time
import queue
import random
import json
import requests

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
                    u.sendall('hello'.encode('utf-8'))


def get_peers(peers_queue):
        while True:
            # Get peers from the catalog
            r = requests.get('http://catalog.cse.nd.edu:9097/query.json')
            address_book = json.JSONDecoder().decode(r.text)
            peers = []

            for address in address_book:
                if 'project' in address:
                    if address['project'] == 'hash_worker':
                        peers.append((str(address['name']), int(address['port'])))

            peers_queue.put(peers)

            time.sleep(10)

'''
def listener(listen_sock, transaction_queue):
    while True:
        msg = listen_sock.recv(1024)
        msg = msg.decode('utf-8', 'strict')
        transaction_queue.put(msg)
'''

def main():

    # Initialize queues
    peers_queue = queue.Queue()
    broadcast_queue = queue.Queue()
    transaction_queue = queue.Queue()

    # Create socket for listening to register with name server
    listen_port = random.randint(9000, 10000)
    ip_addr = socket.gethostbyname(socket.gethostname())
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_addr = socket.gethostbyname(socket.gethostname())

    # Start threads
    name_server_thread = threading.Thread(target=get_peers, daemon=True, args=([peers_queue]))
    name_server_thread.start()

    broadcast_thread = threading.Thread(target=broadcast, daemon=True, args=([broadcast_queue]))
    broadcast_thread.start()

    # Handle requests
    while True:
        if peers_queue.qsize() > 0:
            peers_list = peers_queue.get()
            peers_queue.task_done()
            broadcast_queue.put(peers_list)

        if transaction_queue.qsize() > 0:
            msg = transaction_queue.get()
            transaction_queue.task_done()
            print(msg)

if __name__ == "__main__":
    main()