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
        # print(f"Block ID: {block.index}")
        # print(f"Transactions: {block.transactions}")
        # print(f"Prev Hash: {block.header.prev_hash}")
        # print(f"Curr Hash: {block.header.hash}\n")

        timestamp = datetime.datetime.now()
        # print(f"timestamp: {timestamp}")

        # by adding more zeros we can make this more difficult
        target = 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        # print(f"target: {target}")

        nonce = 0
        hash = ""
        max_nonce = 4294967295 # this is true value, smaller for testing: 4294967295

        mining = True
        while(mining):
            nonce = 0
            # critical to update the timestamp so that we get different hashes
            timestamp = datetime.datetime.now()

            # print(f"Starting again")
            while(nonce < max_nonce):
                # print(f"nonce: {nonce}")

                data_to_hash = (str(timestamp) + str(nonce) + str(block.header.prev_hash) + str(block.transactions)).encode('utf-8')
                # print(f"data to hash: {data_to_hash}")

                encryption = hashlib.sha256()
                encryption.update(data_to_hash)
                hash = encryption.hexdigest()
                # print(hash)
                # print("\n")

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

        # print(f"\n{block.header.timestamp}\nBlock: {block.index}'s hash is: {block.header.hash} from nonce: {block.header.nonce}")

        return


# This is all just a sample to test things working
# blockchain = [Block.genesis_block()]
# prev_block = blockchain[0]
# Block.mine(prev_block)

# print(f"Block ID: {prev_block.index}")
# print(f"Transactions: {prev_block.transactions}")
# print(f"Prev Hash: {prev_block.header.prev_hash}")
# print(f"Curr Hash: {prev_block.header.hash}\n")

# for i in range(0,5):
#     new_block = Block.new_block(prev_block)
#     Block.mine(new_block)
#     blockchain.append(new_block)
#     prev_block = new_block

#     print(f"Block ID: {new_block.index}")
#     print(f"Transactions: {new_block.transactions}")
#     print(f"Prev Hash: {new_block.header.prev_hash}")
#     print(f"Curr Hash: {new_block.header.hash}\n")