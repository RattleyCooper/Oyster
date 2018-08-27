import shlex
from getpass import getpass


class Plugin(object):
    version = 'v1.0'
    invocation = 'sudo '
    enabled = True

    def run(self, server, data):
        args = shlex.split(data)

        if not args:
            pass

        password = getpass('Password: ')
        print('COMMAND: ', 'sudo -password')
        server.send_command('sudo -password', response=True)
        print('PASSWORD: HIDDEN')
        server.send_command(password, response=False)
        print('DATA: ', data)
        server.send_command(data, response=False)
        r = server.get_response()
        print('\n\nRESPONSE: ', r)

