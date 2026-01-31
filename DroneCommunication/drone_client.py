import sys
import threading
import socket
import argparse
import os


class Send(threading.Thread):

    def __init__(self, sock, name, vehicle):
        super().__init__()
        self.sock = sock
        self.name = name
        self.vehicle = vehicle

    def run(self):

        while True:
            message = input('{}: '.format(self.name))

            # Type 'QUIT' to leave the chatroom
            if message == 'QUIT':
                self.sock.sendall('Server: {} has left the chat.'.format(self.name).encode('utf-8'))
                break

            # Send message to server for broadcasting
            else:
                self.sock.sendall('{}: {}'.format(self.name, message).encode('utf-8'))

        print('\nQuitting...')
        self.sock.close()
        sys.exit(0)


class Receive(threading.Thread):

    def __init__(self, sock, name, vehicle):
        super().__init__()
        self.sock = sock
        self.name = name
        self.vehicle = vehicle

    def run(self):

        while True:
            message = self.sock.recv(1024)
            if message:
                print('\r{}\n{}: '.format(message.decode('utf-8'), self.name), end='')
            else:
                # Server has closed the socket, exit the program
                print('\nOh no, we have lost connection to the server!')
                print('\nQuitting...')
                self.sock.close()
                sys.exit(0)


class Client:

    def __init__(self, host, port, vehicle):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.vehicle = vehicle

    def start(self):
        print('Trying to connect to {}:{}...'.format(self.host, self.port))
        self.sock.connect((self.host, self.port))
        print('Successfully connected to {}:{}'.format(self.host, self.port))

        print()
        name = input('Your name: ')

        print()
        print('Commander, {}! Getting ready to send and receive commands...'.format(name))

        # Create send and receive threads
        send = Send(self.sock, name, self.vehicle)
        receive = Receive(self.sock, name, self.vehicle)

        # Start send and receive threads
        send.start()
        receive.start()

        self.sock.sendall('DroneHub: {} has joined the hub.'.format(name).encode('utf-8'))
        print("\rAll set! Leave the chatroom anytime by typing 'QUIT'\n")
        print('{}: '.format(name), end='')


if __name__ == '__main__':
    client = Client(args.host, args.p,1)
    client.start()
