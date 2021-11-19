import pickle
import socket
import sys
import threading
import time
import queue

def receive_broadcast(server_sock, peers_q):
    while True:
        received_peers = pickle.loads(server_sock.recv(1024))
        print('received in thread: {}'.format(received_peers))
        peers_q.put(received_peers)
        print(peers_q)

def accept_connections(my_sock, inbound_q):
    inbound_connection = my_sock.accept()
    inbound_q.put(inbound_connection)

def listen_for_messages(my_sock):
    # probably use the select function here
    while True:
        msg = my_sock.recv(1024)
        print('new message received: '.format(msg))

def connect_to_peers(peers):
    outbound = []
    for peer in peers:
        if peer[0] != socket.gethostbyname(socket.gethostname()):
            # additional check if we already have this connection?
            print('from connect: {}'.format(peer))
            try:
                peer_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                peer_sock.connect((peer[0], int(peer[1])))
                outbound.append(peer_sock)
            except Exception as e:
                print(e)

    return outbound

def main():
    # important lists of information
    peers = []
    outbound_connections = []
    inbound_connections = []

    # connect to rendezvous
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.connect((socket.gethostbyname('student04.cse.nd.edu'), int(sys.argv[1])))

    # create personal socket and send port to server
    my_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_sock.bind(('0.0.0.0', 0))
    my_sock.listen()
    print('listening on: {}'.format(my_sock.getsockname()[1]))
    server_sock.send(str((my_sock.getsockname()[1])).encode())

    # receive current peers from rendezvous
    while True:
        data = server_sock.recv(128).decode()
        print(data)
        if data == 'end':
            break

        ip, port = data.split(' ')
        peers.append((ip, port))

    print('\ndone receiving peers:\n{}'.format(peers))

    # create Queues to share resources
    peers_q = queue.Queue()
    inbound_q = queue.Queue()

    # receive broadcast thread
    receive_broadcast_thread = threading.Thread(target=receive_broadcast, daemon=True, args=([server_sock, peers_q]))
    receive_broadcast_thread.start() 

    # accept connections thread
    accept_connections_thread = threading.Thread(target=accept_connections, daemon=True, args=([my_sock, inbound_q]))
    accept_connections_thread.start()

    # we will also need a thread to listen for messages - needs all inbound sockets
    # listener_thread = threading.Thread(target=listen_for_messages, daemon=True, args=([my_sock]))
    # listener_thread.start()

    # connect to peers received from rendezvous - we will need to do this when receiving updated list
    outbound_connections = connect_to_peers(peers)

    # main program loop
    while True:
        print('\n=====INFO=====')
        print('- Current known peers:')
        for peer in peers:
            print(peer)
        print('\n')
        print('- Current outbound connections:')
        for connection in outbound_connections:
            print(connection)
        print('\n')
        print('- Current inbound connections')
        for connection in inbound_connections:
            print(connection)
        print('\n')
        # get peers from background thread and connect
        if peers_q.empty != True:
            peers = peers_q.get_nowait()
            outbound_connections = connect_to_peers(peers)
        # get inbound connections from accepting thread
        if inbound_q.empty != True:
            inbound_connections = inbound_q.get_nowait()

if __name__ == "__main__":
    main()