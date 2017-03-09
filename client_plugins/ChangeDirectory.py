import sys
from os import chdir
from os.path import expanduser
import shlex


class Plugin(object):
    version = 'v1.0'
    invocation = 'cd '

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
                p, expurs = None, None
                del p
                del expurs
            else:
                _dir = shlex.split(_dir)[0]

            # Change the directory
            chdir(_dir)
            client.send_data('')
            return
        except Exception as err_msg:
            # If we get any errors, send em back!
            err_msg = str(err_msg)
            client.send_data(err_msg + "\n")
            return


