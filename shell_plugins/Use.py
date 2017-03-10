

class Plugin(object):
    """
    Plugin for handling the `use` command.
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

        server.start_client_shell()
        return

