from Block import Block
import random
import datetime
import pprint

def deploy_miners():

    return

txn_list = []
blockchain = []
for i in range(3):
    for j in range(6):
        user = "peer " + str(j) # this will be a machine name or peer name or something
        id = j
        amount = random.randint(0, 35000)
        if random.randint(0, 1) == 0:
            amount = amount * -1
        time = datetime.datetime.now()

        txn = {
            "User": user,
            "ID": id,
            "Amount": amount,
            "Time": str(time)
        }

        txn_list.append(txn)

    # pprint.pprint(txn_list)
    # print("\n")

    if i == 0:
        prev_block = Block.genesis_block(txn_list)
        Block.mine(prev_block)
        blockchain.append(prev_block)
    else:
        new_block = Block.new_block(prev_block, txn_list)
        Block.mine(new_block)
        prev_block = new_block
        blockchain.append(prev_block)

    txn_list = []

for block in blockchain:
    print(f"Block ID: {block.index}")
    print(f"Prev Hash: {block.header.prev_hash}")
    print(f"Curr Hash: {block.header.hash}\n")
        