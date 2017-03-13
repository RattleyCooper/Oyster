import shlex


class Plugin(object):
    version = 'v1.0'
    invocation = 'list'
    enabled = True

    def run(self, server, data):
        print(server.connection_mgr)
        return
