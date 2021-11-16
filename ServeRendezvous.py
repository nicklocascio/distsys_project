#!/usr/bin/bash python3

import sys
from RendezvousServer import Rendezvous

def main():

	if len(sys.argv) != 2:
		return -1

	try:
		port = int(sys.argv[1])
	except:
		return -1

	rend = Rendezvous(port)
	rend.start_service()

if __name__ == '__main__':
	main()
