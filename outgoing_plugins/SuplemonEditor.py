import shlex
from os import remove
from subprocess import Popen


class Plugin(object):
    version = 'v1.0'
    invocation = '# '
    enabled = True

    @staticmethod
    def run(server, data):
        args = shlex.split(data, posix=False)

        # Handle the args.
        if len(args) > 2:
            editor, flags, filepath = args[0], args[1:-1], args[-1]
        elif len(args) == 2:
            editor, filepath = args
        elif len(args) == 1:
            editor, filepath = 'suplemon', args[0]
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
        temp_file = server.connection_mgr.current_connection.get_response()
        if temp_file[:7] == 'ERROR: ':
            print(temp_file)
            return

        # Create a temporary file
        temp_file = '_t_e_m_p_.{}'.format(temp_file.split('.')[-1])

        # Get the file data.
        file_data = server.connection_mgr.current_connection.get_response()
        with open(temp_file, 'w') as f:
            f.write(file_data)
            f.close()

        # Open editor process to edit the file.
        p = Popen(args=[editor, temp_file])
        p.communicate()
        p.terminate()

        # Open the temporary file and send the file data over to the client.
        # If the file was saved after editing, then the changes will be
        # made to the file client-side!
        with open(temp_file, 'r') as f:
            new_file_data = f.read()
            r = server.send_command(new_file_data)
            if r.strip() != 'OK':
                print(r)
                return

        # Remove the temporary file.
        remove(temp_file)
        return







