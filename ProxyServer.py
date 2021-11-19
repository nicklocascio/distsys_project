import socket
import threading
import time
import sys
import pickle

peer_sockets = []
peer_address = []

def broadcast():
    while True:
        for peer in peer_sockets:
            # here we will send to peer_socket, the contents of peer_address
            # need to figure out a better way to send this
            peer.send(pickle.dumps(peer_address))
            print(peer)
        print('\n')
        time.sleep(10)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.bind((socket.gethostname(), int(sys.argv[1])))
        sock.listen()
    except Exception as e:
        sock.close()
        print(e)
        exit(-1)

    # create broadcast thread
    broadcast_thread = threading.Thread(target=broadcast, daemon=True)
    broadcast_thread.start()

    # accept new connections
    while True:
        peer_sock, address = sock.accept()
        print('Connection from {} has been established'.format(address))
        peer_sockets.append(peer_sock)

        peer_port = int(peer_sock.recv(128).decode())
        print('peer listening on port: {}'.format(peer_port))
        peer_address.append((address[0], peer_port))

        # send peer addresses
        for address in peer_address:
            peer_sock.send('{} {}'.format(address[0], address[1]).encode())
            time.sleep(0.005)

        time.sleep(0.5)        
        peer_sock.send(b'end') 

if __name__ == "__main__":
    main()