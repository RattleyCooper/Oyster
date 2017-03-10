import shlex
from time import sleep
from os import getcwd


class Plugin(object):
    version = 'v1.0'
    invocation = 'update'
    enabled = True

    def update_clients(self, server):
        """
        Update all the connected clients using the `update.py` file.

        :return:
        """

        print('Starting update...')
        with open(getcwd() + '/update.py', 'r') as f:
            file_data = ''
            for line in f:
                file_data += line

            _c = "update {}".format(file_data)
            server.connection_mgr.send_commands(_c)
        sleep(.5)
        print('Finished updating clients!')
        server.connection_mgr.close()
        server.connection_mgr.remove_connection(server.connection_mgr.current_connection)
        server.connection_mgr.current_connection = None
        return self

    def run(self, server, data):
        args = shlex.split(data)
        if not args:
            print('`update` requires the `all` argument for now.')

        if args[0] == 'all':
            self.update_clients(server)

