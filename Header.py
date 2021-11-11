class Header:
    def __init__(self, prev_hash, curr_hash):
        self.prev_hash = prev_hash
        self.curr_hash = curr_hash # probably comes from some function in Block
        self.timestamp = None # initialize in mine function
        self.nonce = None # initialize in mine function

    def mine(self):
        return