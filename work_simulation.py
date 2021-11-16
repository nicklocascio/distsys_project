from Block import Block
import random
import datetime
import pprint

def deploy_miners():

    return

blockchain = []
for i in range(3):

    filling = True
    if i == 0:
        block = Block.genesis_block()
    else:
        block = Block.new_block(prev_block)

    j = 0
    while(filling):
        user = "peer " + str(i)
        id = j
        amount = random.randint(0, 35000)
        if random.randint(0,1) == 0:
            amount = amount * -1
        time = datetime.datetime.now()

        txn = {
            "User": user,
            "ID": id,
            "Amount": amount,
            "Time": str(time)
        }

        status = block.add_transaction(txn)

        if status == "Full":
            Block.mine(block)
            blockchain.append(block)
            prev_block = block
            filling = False

        j += 1

for block in blockchain:
    print(f"Block ID: {block.index}")
    # print("Transactions:")
    # pprint.pprint(block.transactions)
    print(f"Prev Hash: {block.header.prev_hash}")
    print(f"Curr Hash: {block.header.hash}\n")
        