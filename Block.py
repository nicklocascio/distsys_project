from os import stat
import time
import Header
import datetime
import hashlib

class Block:
    def __init__(self, index, prev_hash):
        self.index = index
        self.transactions = [] 
        self.header = Header.Header(prev_hash)

    def add_transaction(self, txn):
        self.transactions.append(txn)

        if len(self.transactions) >= 10:
            return "Full"
        else:
            return "Space"

    @staticmethod
    def print(block):
        print('Index: {}'.format(block.index))
        # print('Transactions: {}'.format(block.transactions))
        print('Prev Hash: {}'.format(block.header.prev_hash))
        print('Hash: {}'.format(block.header.hash))
        print('Timestamp: {}'.format(block.header.timestamp))
        print('Nonce: {}\n'.format(block.header.nonce))

    @staticmethod
    def genesis_block():
        return Block(0, "")

    @staticmethod
    def new_block(prev_block):
        index = prev_block.index + 1
        prev_hash = prev_block.header.hash

        return Block(index, prev_hash)

    @staticmethod
    def mine(block):
        timestamp = datetime.datetime.now()

        # by adding more zeros we can make this more difficult
        target = 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

        nonce = 0
        hash = ""
        max_nonce = 4294967295 # max 32 bit integer

        mining = True
        while(mining):
            nonce = 0
            # critical to update the timestamp so that we get different hashes
            timestamp = datetime.datetime.now()

            while(nonce < max_nonce):
                data_to_hash = (str(timestamp) + str(nonce) + str(block.header.prev_hash) + str(block.transactions)).encode('utf-8')

                encryption = hashlib.sha256()
                encryption.update(data_to_hash)
                hash = encryption.hexdigest()

                if int(hash, 16) < target:
                    print(f"\nfound valid hash with nonce {nonce}")
                    print(f"hash: {hash}\n")
                    
                    # update header appropriately
                    block.header.timestamp = timestamp
                    block.header.nonce = nonce
                    block.header.hash = hash

                    # done mining
                    mining = False
                    break

                nonce += 1
        return