import socket
import threading
import time
import random
import json
import requests
import multiprocessing
from queue import Queue
from Block import Block

def broadcast(peers_list, msg):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as u:
        u.bind(('0.0.0.0', 0))
        for peer in peers_list:
            # conditional so we don't send to ourselves
            if socket.gethostbyname(peer[0]) != socket.gethostbyname(socket.gethostname()):
                u.connect(peer)
                u.sendall(msg.encode('utf-8'))

def name_server(listen_port, ip_addr, peers_queue):
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as u:
            
            # register for Catalog
            u.bind(('0.0.0.0', 0))
            u.connect(('catalog.cse.nd.edu', 9097))
            ns_msg = {
                'type' : 'worker',
                'owner' : 'jbigej',
                'port' : listen_port,
                'address' : ip_addr,
                'project' : 'hash_worker'
            }

            u.sendall(json.JSONEncoder().encode(ns_msg).encode(encoding='utf-8'))

            # get peers from the catalog
            r = requests.get('http://catalog.cse.nd.edu:9097/query.json')
            address_book = json.JSONDecoder().decode(r.text)
            peers = []

            for address in address_book:
                if 'project' in address:
                    if address['project'] == 'hash_worker' and address["lastheardfrom"] + 20 > time.time():
                        peers.append((address['name'], address['port']))

            peers_queue.put(peers)

        time.sleep(10)

def listener(listen_sock, transaction_queue, received_blocks_queue, process_queue):
    while True:
        msg = listen_sock.recv(4096)
        msg = msg.decode('utf-8', 'strict')
        msg = json.loads(msg)

        # check for if msg is a block opposed to a transaction
        try:
            if msg["Type"] == "BLOCK":                
                # Parse data from message to build block
                block_data = msg["Block"]
                block_index = block_data["index"]
                block_transactions = block_data["transactions"]
                block_header = block_data["header"]

                block = Block(block_index, block_header["prev_hash"])
                block.transactions = block_transactions
                block.header.hash = block_header["hash"]
                block.header.timestamp = block_header["timestamp"]
                block.header.nonce = block_header["nonce"]

                received_blocks_queue.put((msg["Worker"], block))

                while process_queue.qsize() > 0:
                    # Terminate all processes in queue: should only be one at this point
                    process = process_queue.get()
                    process.terminate()
                    process_queue.task_done()

                continue
            elif msg["Type"] == "TXN":
                transaction_queue.put(msg["Txn"])
        except Exception:
            None

def mine(curr_block, return_dict):
    Block.mine(curr_block)
    return_dict["block"] = curr_block 

def main():
    # create socket for listening to register with name server
    listen_port = random.randint(9000, 10000)
    ip_addr = socket.gethostbyname(socket.gethostname())
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.bind(('0.0.0.0', listen_port))

    # Queues for resource sharing
    peers_queue = Queue()
    transaction_queue = Queue()
    received_blocks_queue = Queue()
    process_queue = Queue()

    # Create name server thread
    name_server_thread = threading.Thread(target=name_server, daemon=True, args=([listen_port, ip_addr, peers_queue]))
    name_server_thread.start()

    # Create listening thread
    listener_thread = threading.Thread(target=listener, daemon=True, args=([listen_sock, transaction_queue, received_blocks_queue, process_queue]))
    listener_thread.start()

    # Initialize peers and blockchain lists and transaction ledger
    peers_list = []
    txn_ledger = {}
    local_blockchain = []
    chains = {
        "local": local_blockchain
    }
    curr_block = Block.genesis_block()

    # Main program loop to pull transactions from queue and work on mining
    while True:

        if peers_queue.qsize() > 0:
            peers_list = peers_queue.get()
            peers_queue.task_done()
        
        if received_blocks_queue.qsize() > 0:
            worker, block = received_blocks_queue.get()
            print('\nBlock from worker: {}'.format(worker))
            Block.print(block)

            if block.index >= curr_block.index:
                try:
                    chains['local'].append(block)
                except:
                    chains['local'] = [block]
                prev_block = block
                curr_block = Block.new_block(prev_block)
            
            try:
                chains[worker].append(block)
            except Exception:
                chains[worker] = [block]

            print('=====BLOCKCHAIN=====')
            for block in chains["local"]:
                Block.print(block)            

        if transaction_queue.qsize() > 0 and received_blocks_queue.qsize() == 0 and len(curr_block.transactions) < 10:
            msg = transaction_queue.get()
            print('Txn: {}'.format(msg))
            transaction_queue.task_done()

            # verify transaction before inserting into block - this is only local verification with respect to what worker knows
            amount = msg["Amount"]
            verified = False
            # "withdrawal"
            if amount < 0:
                try:
                    user_balance = txn_ledger[msg["User"]]
                    if user_balance + amount < 0:
                        print('txn results in balance of {}, discarding'.format(user_balance + amount))
                    else:
                        txn_ledger[msg["User"]] = user_balance + amount
                        verified = True
                except Exception:
                    print('new user withdrawing right away, not valid')
            # "deposit"
            else:
                try:
                    txn_ledger[msg["User"]] = txn_ledger[msg["User"]] + amount
                    verified = True
                except Exception:
                    print('adding new user: {}'.format(msg["User"]))
                    txn_ledger[msg["User"]] = amount
                    verified = True

            # Insert verified transaction into block and check if we need to mine
            if verified:
                status = curr_block.add_transaction(msg)
                if status == "Full":
                    manager = multiprocessing.Manager()
                    return_dict = manager.dict()
                    p = multiprocessing.Process(target=mine, args=([curr_block, return_dict]))
                    process_queue.put(p)
                    p.start()
                    p.join()

                    # dequeue process that solved the block
                    if process_queue.qsize() > 0:
                        p = process_queue.get()
                        process_queue.task_done()
                    
                    # try/except block if process is interrupted
                    try:
                        curr_block = return_dict.values()[0]
                        Block.print(curr_block)

                        # broadcast block to other peers
                        msg = {
                            "Type": "BLOCK",
                            "Worker": socket.gethostname(),
                            "Block": {
                                "index": curr_block.index,
                                "transactions": curr_block.transactions,
                                "header": {
                                    "prev_hash": curr_block.header.prev_hash,
                                    "hash": curr_block.header.hash,
                                    "timestamp": str(curr_block.header.timestamp),
                                    "nonce": curr_block.header.nonce
                                }
                            }
                        }
                        msg = json.dumps(msg)
                        broadcast(peers_list, msg)

                        # add to blockchain and create new block
                        local_blockchain.append(curr_block)
                        chains["local"] = local_blockchain
                        prev_block = curr_block
                        curr_block = Block.new_block(prev_block)

                        print('=====BLOCKCHAIN=====')
                        for block in chains["local"]:
                            Block.print(block)

                    except Exception:
                        None
                  
if __name__ == "__main__":
    main()