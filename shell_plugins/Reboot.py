

class Plugin(object):
    version = 'v1.0'
    invocation = 'reboot'
    enabled = True

    def run(self, server, data):
        print('Rebooting...')
        server.reboot_self()
        return

