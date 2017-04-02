import shlex
from os import getcwd
from os.path import realpath, expanduser


class Plugin(object):
    """
    This plugin is designed for editing files!

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
    def run(client, data):
        args = shlex.split(data)

        if not args:
            client.server_print('Did not specify a file to edit.')

        # Get the filepath and open the file.
        # if there is no file, then set the
        # file data to an empty byte string
        # so a new empty file is created.
        if args[0][:2] == '~/':
            filepath = expanduser(args[0])
        elif '/' not in args[0] and '\\' not in args[0]:
            filepath = getcwd() + '/' + args[0]

        try:
            with open(filepath, 'rb') as f:
                file_data = f.read()
        except Exception as err:
            print(str(err))
            file_data = b''

        # Tell the server that the file was read correctly.
        client.send_data('OK')

        # Send the filename
        filename = filepath.split('/')[-1] if '/' in filepath else filepath.split('\\')[-1]
        client.send_data(filename)

        # Send the original file data.
        client.send_data(file_data, encode=False)

        # Receive the new file data.
        new_file_data = client.receive_data(decode=False)

        # Write the new file data to a file.
        with open(filepath, 'wb') as f:
            f.write(new_file_data)

        # Tell the server the new file data has been written.
        client.send_data('OK')
        return
