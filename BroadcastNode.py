#!/usr/bin/bash python3

import sys
import json
from Node import Node

def main():
    if len(sys.argv) != 4:
        return -1

    try:
        host = str(sys.argv[1])
    except:
        return -1

    try:
        port = int(sys.argv[2])
    except:
        return -1

    try:
        self_port = int(sys.argv[3])
    except:
        return -1
        
    node = Node(host, port, self_port)
    node.broadcast()

if __name__ == '__main__':
	main()
