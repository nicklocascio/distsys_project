class Header:
    def __init__(self, prev_hash):
        self.prev_hash = prev_hash
        self.hash = None # set in mine function
        self.timestamp = None # initialize in mine function
        self.nonce = None # initialize in mine function