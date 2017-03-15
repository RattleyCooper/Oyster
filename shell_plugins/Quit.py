from common import ThreadControl
from common import LoopControl


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
        server.connection_mgr.close_all_connections()
        thread_control = ThreadControl()

        thread_control.control_dictionary = {
            'ACCEPT_CONNECTIONS': False
        }
        thread_control.loop_control = LoopControl().should_break()

        return thread_control
