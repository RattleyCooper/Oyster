import shlex
from os.path import expanduser


class Plugin(object):
    """
    The plugin that handles the `get` command.
    """

    version = 'v1.0'
    # invocation must be set to the command that invokes the plugin.
    invocation = 'get '
    enabled = True

    # The run method must be set on the Plugin object in order to do anything
    def run(self, server, data):
        """
        The run method is called from within the server.py file when needed.

        The `server` argument is the instance of the `Server` object.  The
        `data` argument will be any additional data that was sent along with
        the command.  It's up to the plugin writer to parse the data.

        :param server:
        :param data:
        :return:
        """

        data = data.strip()
        # Split up the filepaths using shlex.
        remote_filepath, local_filepath = shlex.split(data)

        # Send a command to the client.  tell it that a file
        # response is expected by giving it a filepath to
        # save the data to.
        response = server.connection_mgr.send_command(
            'get {}'.format(remote_filepath),
            file_response=expanduser(local_filepath)
        )

        print('< < {} > >'.format(response))
        if 'Errno' not in response:
            print('< File Stashed: {} >'.format(expanduser(local_filepath)))
        return
