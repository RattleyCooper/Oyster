from common import LoopControl
from client import Client


class Plugin(object):
    """
    Quit v1.0

    Shutdown the server.py script.

    Invocations:

        quit
        exit
        shutdown

    Commands:

        quit/exit/shutdown      -   Any of the 3 commands will shutdown the
                                    server.py script

    Example:

        Oyster> quit
        < Shutdown complete! >
    """

    version = 'v1.0'
    invocation = ['quit', 'exit', 'shutdown']
    enabled = True

    def run(self, server, data):
        print('< Shutting down. >')

        server.shutdown_event.set()
        # Boot up a client in order to stop the server's listener thread's
        # self.sock.accept() call from blocking and allow the ShutdownEvent
        # to be processed.
        Client(port=server.port, echo=False)

        return LoopControl().should_break()
