

class Plugin(object):
    """
    Reboot v1.0

    Reboot the server.py file.

    Invocation:

        reboot

    Commands:

        reboot              -   Reboot the server.py script.

    Example:

        Oyster> reboot
    """

    version = 'v1.0'
    invocation = 'reboot'
    enabled = True

    @staticmethod
    def run(server, data):
        print('Rebooting...')
        server.reboot_self()
        return

