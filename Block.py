import Header
import datetime
import hashlib

class Block:
    def __init__(self, index, timestamp, transactions, prev_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions # this will probably end up being a list
        self.prev_hash = prev_hash
        self.hash = self.generate_hash()

    def add_transaction(self, curr_block):
        '''
        Need to figure out the format of a transaction, here are some initial thoughts:

        {
            "User": "Peer_Name",
            "ID": ID,
            "Amount": 35,
            "Timestamp": ...,

        }
        '''
        return

    def generate_hash(self):
        encryption = hashlib.sha256()
        encryption.update((str(self.index) + str(self.timestamp) + str(self.transactions) + str(self.prev_hash)).encode('utf-8'))

        return encryption.hexdigest()

    @staticmethod
    def genesis_block():
        return Block(0, datetime.datetime.now(), "genesis transaction", "")

    @staticmethod
    def new_block(prev_block):
        index = prev_block.index + 1
        timestamp = datetime.datetime.now()
        transactions = "Transaction " + str(index)
        prev_hash = prev_block.hash

        return Block(index, timestamp, transactions, prev_hash)

blockchain = [Block.genesis_block()]
prev_block = blockchain[0]

print(f"Block ID: {prev_block.index}")
print(f"Timestamp: {prev_block.timestamp}")
print(f"Transactions: {prev_block.transactions}")
print(f"Hash of prev: {prev_block.prev_hash}")
print(f"Hash of this block: {prev_block.hash}\n")

for i in range(0,5):
    new_block = Block.new_block(prev_block)
    blockchain.append(new_block)
    prev_block = new_block

    print(f"Block ID: {new_block.index}")
    print(f"Timestamp: {new_block.timestamp}")
    print(f"Transactions: {new_block.transactions}")
    print(f"Hash of prev: {new_block.prev_hash}")
    print(f"Hash of this block: {new_block.hash}\n")