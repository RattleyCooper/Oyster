

class Plugin(object):
    """
    ListConnections v1.0

    List all of the current connections in the connection manager.

    Invocation:

        list

    Commands:

        list              -   List all connections in the connection manager.

    Example:

        Oyster> list
        -------------- Clients --------------
        [0]   127.0.0.1   63490
    """

    version = 'v1.0'
    invocation = 'list'
    enabled = True

    @staticmethod
    def run(server, data):
        print(server.connection_mgr)
        return
