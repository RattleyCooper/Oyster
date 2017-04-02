import shlex
from os import getcwd
from os.path import expanduser


class Plugin(object):
    """
    Editor v1.0 - Client-Side

    This plugin is designed for using local server-side tools to edit client-side files!

    As it stands, only small files are supported.

    Any file that can be opened and edited from the command line should be editable!

    If you have `suplemon` installed locally, you can use the syntax:

        > # {filepath}

    to open any text file for editing without having to type the name of the editor.

    For more complicated editing(audio, pictures, video, etc), you can tag the
    filename in question with `<f> and provide more arguments.

    Example of using imagemagick to resize a picture:

        `/Users/user/Pictures> magick ~/Pictures/drink.jpg -resize 50% drink.jpg`

      becomes

        `/Users/user/Pictures> # magick <f>~/Pictures/drink.jpg -resize 50% <f>drink.jpg`

    If you ran the first example, it would try to use imagemagick on the client machine
    whereas the second example would grab the filedata(for the first tagged filename in
    the command), from the client machine and then use imagemagick to edit it locally
    before sending the modified data back to the client.
    """

    version = 'v1.0'
    invocation = '# '
    enabled = True

    @staticmethod
    def run(client, data):
        args = shlex.split(data)
        # Step 1.
        # The initial command sent by the `outgoing_plugins/Editor.py` file is what
        # triggered this plugin to run, so since the `outgoing_plugins/Editor.py`
        # file expects a response, we need to send one before moving on to the
        # next step.
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
        # Step 1 Done!

        # Step 2.
        # Now the server expects a filename to be sent over.
        filename = filepath.split('/')[-1] if '/' in filepath else filepath.split('\\')[-1]
        client.send_data(filename)

        # Step 3.
        # Send the original file data.
        client.send_data(file_data, encode=False)

        # Step 4.
        # Receive the new file data.
        new_file_data = client.receive_data(decode=False)

        # Write the new file data to a file.
        with open(filepath, 'wb') as f:
            f.write(new_file_data)

        # Tell the server the new file data has been written.
        client.send_data('OK')
        # Step 4 Done!
        return
