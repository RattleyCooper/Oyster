import shlex
import sys
import socket
import subprocess
from os.path import realpath


class Plugin(object):
    version = 'v1.0'
    invocation = 'client '
    enabled = True

    def run(self, client, data):
        args = shlex.split(data)

        if not args:
            client.server_print('< The `client` command requires an argument. >')

        # Set an attribute on the Client instance.
        if args[0] == '-s':
            try:
                key, value = args[1], args[2]
            except IndexError:
                client.server_print('< `setattr` requires a `key` and `value`. >')
                return
            try:
                setattr(client, key, value)
                client.server_print('< Client attribute "{}" set to "{}". >'.format(key, value))
            except AttributeError:
                client.server_print('< Client has no attribute, "{}". >'.format(key))

            return

        # Restart the `client.py` script.
        if args[0] == '-r':
            client.send_data('')
            Plugin.reboot_client(client)
            sys.exit()

    @staticmethod
    def reboot_client(client):
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
            'session_id={}'.format(client.session_id),
            'echo={}'.format(client.echo)
        ]

        # Try to use subprocess to reboot.  If there is a permissions error,
        # use execv to try to achieve the same thing.
        try:
            popen_rc = [sys.executable] + list((sys.argv[0],)) + rc[1:]
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

