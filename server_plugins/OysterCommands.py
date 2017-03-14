import shlex
from common import LoopControl


class Plugin(object):
    version = 'v1.0'
    invocation = 'oyster '
    enabled = True
    
    def run(self, server, data):
        args = shlex.split(data)
        lc = LoopControl()
        
        if not args:
            return

        if args[0] == 'shell-reboot':
            try:
                server.connection_mgr.send_command(self.invocation + data)
                server.connection_mgr.remove_connection(server.connection_mgr.current_connection)
                server.connection_mgr.current_connection = None
            except BrokenPipeError as err_msg:
                server.connection_mgr.remove_connection(server.connection_mgr.current_connection)
                server.connection_mgr.current_connection = None
                return lc.should_break()
            return lc.should_break()
