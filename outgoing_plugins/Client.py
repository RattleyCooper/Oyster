import shlex
from common import safe_input


class Plugin(object):
    version = 'v1.0'
    invocation = 'client '
    enabled = True

    def run(self, server, data):
        args = shlex.split(data)

        if not args:
            pass

        if args[0] == '-i':
            server.connection_mgr.send_command('client -i', get_cwd=False)
            while True:
                command = safe_input('>>> ')
                if command == 'exit()':
                    server.connection_mgr.send_command(command, get_cwd=False)
                    break
                response = server.connection_mgr.send_command(command, get_cwd=False)
                if response.strip():
                    print(response.strip())
            return

        print(server.connection_mgr.send_command('client {}'.format(data)), end='')

