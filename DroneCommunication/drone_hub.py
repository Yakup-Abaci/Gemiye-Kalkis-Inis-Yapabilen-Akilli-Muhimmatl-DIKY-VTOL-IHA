import sys
import threading
import socket
import argparse
import os


class DroneHub(threading.Thread):

    def __init__(self, host, port):
        super().__init__()

        self.connections = []
        self.host = host
        self.port = port

    def run(self):  # logic of threading happening here

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        sock.listen(2)
        print('Listening at', sock.getsockname())

        while True:
            # Accept new connection
            sc, sockname = sock.accept()
            print('Accepted a new connection from {} to {}'.format(sc.getpeername(), sc.getsockname()))

            # Create new thread
            server_socket = HubSocket(sc, sockname, self)

            # Start new thread
            server_socket.start()

            # Add thread to active connections
            self.connections.append(server_socket)
            print('Ready to communicate with drone from', sc.getpeername())

    def broadcast(self, message, source):

        for connection in self.connections:

            # Send to all connected clients except the source client
            if connection.sockname != source:
                connection.send(message)


class HubSocket(threading.Thread):

    def __init__(self, sc, sockname, serv):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = serv

    def run(self):

        while True:
            message = self.sc.recv(1024).decode('utf-8')
            if message:
                print('{} sent command: {!r}'.format(self.sockname, message))
                self.server.broadcast(message, self.sockname)
            else:
                # Client has closed the socket, exit the thread
                print('{} has closed the connection'.format(self.sockname))
                self.sc.close()
                #self.server.remove_connection(self)
                return

    def send(self, message):
        self.sc.sendall(message.encode('utf-8'))




if __name__ == '__main__':
    # Create and start server thread
    server = DroneHub(args.host, args.p)
    server.start()

