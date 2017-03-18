from common import LoopEvent


class Plugin(object):
    """
    Quit v1.0

    Quit out of a client shell.

    Invocation:

        quit
        exit

    Commands:

        quit/exit           -   Shut down a client shell.

    Example:

        Oyster> quit
    """

    version = 'v1.0'
    invocation = ['quit', 'exit']
    enabled = True

    def run(self, server, data):
        # print('< Detaching from client... >')

        try:
            server.connection_mgr.close_connection(server.connection_mgr.current_connection.ip)
        except (BrokenPipeError, OSError) as err_msg:
            server.connection_mgr.remove_connection(server.connection_mgr.current_connection)
            server.connection_mgr.current_connection = None
            return LoopEvent.should_break()

        server.connection_mgr.remove_connection(server.connection_mgr.current_connection)
        server.connection_mgr.current_connection = None

        return LoopEvent.should_break()
