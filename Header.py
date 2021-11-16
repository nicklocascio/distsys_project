class Header:
    def __init__(self, prev_hash):
        self.prev_hash = prev_hash
        self.hash = None # probably comes from some function in Block
        self.timestamp = None # initialize in mine function
        self.nonce = None # initialize in mine function