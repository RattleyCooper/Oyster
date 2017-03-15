import shlex
from time import sleep
from os import getcwd


class Plugin(object):
    """
    ClientUpdate v1.0

    Update a client remotely.

    Invocation:

        update

    Commands:

        update all              -   Update all connected clients using the
                                    `update.py` script in the Oyster
                                    directory.

    Example:

        Oyster> update all
        < Starting script upload. >
        < Finished updating clients! >

    todo: Make this do a full update :D
    """

    version = 'v1.0'
    invocation = 'update'
    enabled = True

    @staticmethod
    def run(server, data):
        args = shlex.split(data)
        if not args:
            print('< `update` requires the `all` argument for now. >')
            return

        if args[0] == 'all':
            Plugin.update_clients(server)
            return

    @staticmethod
    def update_clients(server):
        """
        Update all the connected clients using the `update.py` file.

        :return:
        """

        print('< Starting script upload. >')
        with open(getcwd() + '/update.py', 'r') as f:
            file_data = ''
            for line in f:
                file_data += line

            _c = "update {}".format(file_data)
            server.connection_mgr.send_commands(_c)
        sleep(.5)

        server.connection_mgr.connections = {}
        server.connection_mgr.current_connection = None

        print('< Finished updating clients! >')

        return

