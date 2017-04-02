import shlex
from common import safe_input


class Plugin(object):
    """
    Client v1.0

    Handle commands that have to do with the `Client` object.

    Invocation:

        client

    Commands:

        client -i               -   Enter an interactive Python console.
                                    Use `exit()` to exit.  The `Client`
                                    object is accessible through the
                                    `client` variable when in the
                                    console.  Any changes will persist.

    Example:

        <127.0.0.1> /Users/user/Oyster> client -i
        |>>> client.port
        6667
        |>>> client.port = 6668
        |>>> x
        Traceback (most recent call last):
          File "/Users/sanctuary/Dropbox/Python/Oyster/common.py", line 114, in run_plugin
            result = plugin.run(self, command)
        TypeError: run() missing 1 required positional argument: 'data'

        During handling of the above exception, another exception occurred:

        Traceback (most recent call last):
          File "< Interactive Python Console >", line 1, in <module>
        NameError: name 'x' is not defined
        |>>>
    """

    version = 'v1.0'
    invocation = 'client'
    enabled = True

    @staticmethod
    def run(server, data):
        args = shlex.split(data)

        if not args:
            pass

        if args[0] == '-i':
            Plugin.start_python_shell(server)

        # Send the command to the client if it doesn't need to be intercepted!
        print(server.connection_mgr.send_command('client {}'.format(data)), end='')

    @staticmethod
    def start_python_shell(server):
        # Tell the client we want an interactive python shell.
        server.connection_mgr.send_command('client -i')
        while True:
            # Ask for a command to send to the client.
            command = safe_input('>>> ')
            # Handle the exit() command if needed.
            if command == 'exit()':
                server.connection_mgr.send_command(command)
                break
            # Send the command to the client and print the response..
            response = server.connection_mgr.send_command(command)
            if response.strip():
                print(response.strip())
        return
