#!/usr/bin/bash python3

import sys
import select
import json
import socket

class Rendezvous():
    def __init__(self, port):
        self.port = port
        self.host = ''
        self.peers = []
        self.peers_log = {}

    def handle_recv(self, sock):
        msg = ''
        try:
            msg = sock[0].recv(1024)

            if not len(msg):
                return -1
            
            req = json.JSONDecoder().decode(msg.decode('utf-8', 'strict'))
        except:
            return -1

        req = json.JSONDecoder().decode(msg.decode('utf-8', 'strict'))
        if req['method'] == 'CONNECT':
            if req['HOST'] not in self.peers_log:
                self.peers_log[req['HOST']] = set()
                self.peers_log[req['HOST']].add(req['PORT'])
                self.peers.append((req['HOST'], req['PORT']))
            else:
                if req['PORT'] not in self.peers_log[req['HOST']]:
                    self.peers_log[req['HOST']].add(req['PORT'])
                    self.peers.append((req['HOST'], req['PORT']))

            resp = {'PEERS': []}

            for peer in self.peers:
                resp['PEERS'].append(peer)
            print(resp)
            enc_resp = json.JSONEncoder().encode(resp).encode(encoding='utf-8')
            sock[0].sendall(enc_resp)


    def start_service(self):
        conn_sockets = {}
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        event_poll = select.poll()
        
        try:
            s.bind(('0.0.0.0', self.port))
            s.listen()

            self.port = s.getsockname()[1]
            self.host = socket.gethostname()

            print('Host: ', self.host)
            print('Port: ', self.port)

            s.setblocking(False)
            event_poll.register(s, select.POLLIN)
            conn_sockets[s.fileno()] = (s, None)

            while s:
                fdEvents = event_poll.poll(1000)

                if len(fdEvents) != 0:
                    for fd, event in fdEvents:
                        sock = conn_sockets[fd]

                        if event & (select.POLLHUP | select.POLLERR | select.POLLNVAL):
                            event_poll.unregister(fd)
                            del conn_sockets[fd]
                        elif sock[0] is s:
                            new_conn, new_addr = s.accept()
                            new_conn.setblocking(False)
                            new_fd = new_conn.fileno()
                            conn_sockets[new_fd] = (new_conn, new_addr)
                            event_poll.register(new_fd, select.POLLIN)
                            event_poll.register(fd, select.POLLIN)
                            print('new connection')
                        elif event & select.POLLIN:
                            self.handle_recv(sock)
        
        except socket.error as e:
            print(e)
            del conn_sockets[s.fileno()]
