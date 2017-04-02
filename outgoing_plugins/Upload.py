from os.path import expanduser
from base64 import b64encode
import shlex


def safe_input(display_string):
    """
    Get input from user.  Should work with python 2.7 and 3.x

    :param display_string:
    :return:
    """

    try:
        x = raw_input(display_string)
    except NameError:
        x = input(display_string)

    return x


class Plugin(object):
    """
    Upload v1.0

    Upload a file to the currently connected client.

    Invocation:

        upload

    Commands:

        The Upload plugin doesn't follow normal conventions.  A filepath must be sent to the server,
        then any data after that will be considered to be the file being uploaded.

        upload filepath {filepath}     -   List all connections in the connection manager.

    Example:

        Oyster> list
        -------------- Clients --------------
        [0]   127.0.0.1   63490
    """

    version = 'v1.0'
    invocation = 'upload '
    enabled = True

    def run(self, server, data):
        """
        Handle a file upload.

        :param server:
        :param data:
        :return:
        """

        data = data.strip()

        filepaths = None if len(data) < 1 else data

        if server.connection_mgr.current_connection is None:
            print(server.connection_mgr)
            connection_id = safe_input('< Enter Client IP or Index > ')
        else:
            connection_id = None

        # Handle the filepaths variable
        if filepaths is None:

            local_filepath = expanduser(safe_input('< Local File Path >'))
            remote_filepath = safe_input('< Remote File Path >')

        else:
            try:
                local_filepath, remote_filepath = shlex.split(filepaths)
                local_filepath = expanduser(local_filepath)
            except ValueError as err_msg:
                print('ValueError handling upload:', err_msg)
                return

        if connection_id is not None:
            connection = server.connection_mgr[connection_id]
        else:
            connection = server.connection_mgr.current_connection

        print(connection.send_command('upload filepath {}'.format(remote_filepath)))

        r = None
        try:
            with open(expanduser(local_filepath), 'rb') as f:
                data = b64encode(f.read())
                # r = connection.send_command('upload data')
                r = '\n' + connection.send_command(data, encode=False)
        except FileNotFoundError as err_msg:
            print(err_msg)

        print(r)
        return

