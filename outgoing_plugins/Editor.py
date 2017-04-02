import shlex
from os import remove
from os.path import expanduser
from subprocess import Popen


class Plugin(object):
    """
    Editor v1.0 - Server-Side

    This plugin is designed for using local server-side tools to edit client-side files!

    As it stands, only small files are supported.

    Any file that can be opened and edited from the command line with the following syntax:

        > {program} {flags} {filepath}

    Can be edited using the syntax:

        > # {program} {flags} {filepath}

    It is important that {program} is the first argument, after the `#`,
    and {filepath} is the last argument.
    """

    version = 'v1.0'
    invocation = '# '
    enabled = True

    @staticmethod
    def run(server, data):
        args = shlex.split(data, posix=False)

        # Handle the args.
        if len(args) > 2:
            editor, filepath = args[0], args[-1]
        elif len(args) == 2:
            editor, filepath = args
        elif len(args) == 1:
            editor, filepath, flags = 'suplemon', args[0], []
            args.insert(0, 'suplemon')
        else:
            print('< Editing requires a filepath in order to function. >')
            return

        # Send the file name over to the client
        r = server.send_command('{}{}'.format(Plugin.invocation, filepath))

        # If the client doesn't respond with "OK"
        # then there was a problem opening the file
        # so print the response.
        if r.strip() != 'OK':
            print(r)
            return

        # Receive the filename.
        temp_file_name = server.connection_mgr.current_connection.get_response()
        if temp_file_name[:7] == 'ERROR: ':
            print(temp_file_name)
            return

        # Create a temporary file
        temp_file_name = '_e_d_i_t__t_e_m_p_.{}'.format(temp_file_name.split('.')[-1])

        # Get the file data.
        file_data = server.connection_mgr.current_connection.get_response(decode=False)
        with open(temp_file_name, 'wb') as f:
            f.write(file_data)
            f.close()

        while True:
            # Open editor process to edit the file.
            # get the index of the filepath
            try:
                findex = args.index(filepath)
            except ValueError:
                break

            # insert the temporary filename at
            # the index.
            args.insert(findex, temp_file_name)

            # remove the original filepath
            args.remove(filepath)

        # Open the process.
        p = Popen(args=args)
        p.communicate()
        p.terminate()

        # Open the temporary file and send the file data over to the client.
        # If the file was saved after editing, then the changes will be
        # made to the file client-side!
        with open(temp_file_name, 'rb') as f:
            new_file_data = f.read()
            r = server.send_command(new_file_data, encode=False)
            if r.strip() != 'OK':
                print(r)
                return

        # Remove the temporary file.
        remove(temp_file_name)
        return







