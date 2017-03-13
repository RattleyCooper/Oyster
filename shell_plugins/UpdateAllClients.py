from time import sleep


class Plugin(object):
    version = 'v1.0'
    invocation = 'update all'
    enabled = True

    def run(self, server, data):
        """
        Update all the connected clients using the `update.py` file.

        :return:
        """

        print('Starting script upload...')
        with open('update.py', 'r') as f:
            file_data = ''
            for line in f:
                file_data += line

            _c = "update {}".format(file_data)
            print(server.connection_mgr.send_commands(_c))
        sleep(.5)
        server.connection_mgr.close()
        server.connection_mgr.remove_connection(server.connection_mgr.current_connection)
        server.connection_mgr.current_connection = None
        print('Finished uploading \'update.py\' to client.')
        return self
