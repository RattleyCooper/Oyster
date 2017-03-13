from server import LoopController


class Plugin(object):
    version = 'v1.'
    invocation = ['quit', 'exit']
    enabled = True

    def run(self, server, data):
        print('Detaching from client...')

        lc = LoopController()

        try:
            server.connection_mgr.close()
        except (BrokenPipeError, OSError) as err_msg:
            server.connection_mgr.remove_connection(server.connection_mgr.current_connection)
            server.connection_mgr.current_connection = None

            lc.should_break = True
            return lc

        server.connection_mgr.remove_connection(server.connection_mgr.current_connection)
        server.connection_mgr.current_connection = None

        lc.should_break = True
        return lc
