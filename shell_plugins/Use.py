

class Plugin(object):
    """
    Use v1.0

    Start a client shell for the given connection.

    Invocation:

        use

    Commands:

        use {index  }       -   Use the given connection by {index}.
                                Get a list of {index}es using the
                                `list` command.

        use {ip address}    -   Use the given connection by {ip address}.

    Example:

        Oyster> use 0
        <127.0.0.1> /Users/user/Oyster>
    """

    version = 'v1.0'
    invocation = 'use'
    enabled = True

    def run(self, server, data):
        # Drop into the given connection's shell.

        data = data.strip()
        if data.lower() == 'none':
            server.connection_mgr.use_connection(None)
        # Use a connection.
        r = server.connection_mgr.use_connection(data)
        if r is None:
            print('Could not connect to client with given information.')
            return

        c = None
        # c =[
        #     'cd ~/Music/iTunes',
        #     'cd iTunes\ Media',
        #     'cd Music',
        #     'cd Grimes',
        #     'cd Art\ Angels'
        # ]
        server.start_client_shell(commands=c)
        return

