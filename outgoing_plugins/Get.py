import shlex
from os.path import expanduser


class Plugin(object):
    """
    Get v1.0

    The `get` command downloads a file(or zipped folder) from
    the currently connected client.

    Invocation:

        get

    Commands:

        get {remote_filepath} {local_filepath}      -   Get a file from the client's
                                                        {remote_filepath} and store
                                                        it at the specified
                                                        {local_filepath}.

    Example:

        < 127.0.0.1 > /Users/user/Oyster> get "/Users/user name/Dropbox" db.zip
    """

    version = 'v1.0'
    # invocation must be set to the command that invokes the plugin.
    invocation = 'get'
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

        print('< {} >'.format(response))
        if 'Errno' not in response:
            print('< File Stashed: {} >'.format(expanduser(local_filepath)))
        return
