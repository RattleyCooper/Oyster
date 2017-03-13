import shlex


class Plugin(object):
    version = 'v1.0'
    invocation = 'update all'
    enabled = True

    def run(self, server, data):
        server.update_clients()
        return
