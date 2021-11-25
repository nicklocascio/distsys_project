import pickle
import socket
import sys
import threading
import time
import queue
import random
import json
import requests

def broadcast(peers_list):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as u:
        u.bind(('0.0.0.0', 0))
        for peer in peers_list:
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
                    if address['project'] == 'hash_worker' and address["lastheardfrom"] + 20 > time.time():
                        peers.append((str(address['name']), int(address['port'])))

            peers_queue.put(peers)

            time.sleep(10)


def main():
    # Start name server thread
    peers_queue = queue.Queue()
    name_server_thread = threading.Thread(target=get_peers, daemon=True, args=([peers_queue]))
    name_server_thread.start()

    peers_list = []

    # Send transactions in a loop while pulling new peers from thread
    while True:
        if peers_queue.qsize() > 0:
            peers_list = peers_queue.get()
            peers_queue.task_done()

        broadcast(peers_list)
        time.sleep(1)

if __name__ == "__main__":
    main()