# ~*
# This is a nice plugin to give a little overview of the basic plugin api.
# The `client_plugins/Editor.py` file is the companion plugin to this file
# so make sure to follow along there as well.
#
# `Plugin`s call their `run` method when commands are executed in certain
# prompts in the Oyster Shell
#
# Any file dropped in a plugins folder will be treated as a plugin.
# Any file dropped in a plugins folder must be contain object named
# `Plugin`, and should inherit from `object`.  Each `Plugin` is
# required to have the following static attributes:
#
#     version           -   The version of the plugin
#     invocation        -   The command that invokes the `run` method
#                            on the `Plugin` object.
#     enabled           -   Whether the plugin is enabled(True or False)
#
# A `run` method is required as well.  It doesn't have to be static
# but if it is then the `Plugin` doesn't have to be instantiated by
# the Oyster Shell.  The `run` method must have either a `server`(or
# `client` for client plugins) instance as the first argument, and
# `data` as the second argument.  `data` will be any arguments that
# were passed along with the command that invoked the `Plugin`.
# It is up to the author of the plugin to handle parsing the
# data.  I have a live template in pycharm so I can type `oyp`,
# hit ENTER, and then start filling in the needed attributes.
#
# Read over the comments throughout the 2 `Editor.py` files.
# I labeled some "Steps" to show how the plugins communicate
# with each other.
# ~*~*

import shlex
from os import remove
from subprocess import Popen
from common import safe_input


class Plugin(object):
    """
    Editor v1.0 - Server-Side

    This plugin is designed for using local server-side tools to edit client-side files!

    As it stands, only small files are supported.

    Any file that can be opened and edited from the command line should be editable!

    If you have `suplemon` installed locally, you can use the syntax:

        > # {filepath}

    to open any text file for editing without having to type the name of the editor.

    For more complicated editing(audio, pictures, video, etc), you can tag the
    filename in question with `<f>` and provide more arguments.

    Example of using imagemagick to resize a picture:

        `/Users/user/Pictures> magick ~/Pictures/drink.jpg -resize 50% drink.jpg`

      becomes

        `/Users/user/Pictures> # magick <f>~/Pictures/drink.jpg -resize 50% <f>drink.jpg`

    If you ran the first example, it would try to use imagemagick on the client machine
    whereas the second example would grab the filedata(for the first tagged filename in
    the command), from the client machine and then use imagemagick to edit it locally
    before sending the modified data back to the client.

    Options:

        -p              -   If you are running a more complex edit and the program
                            you are using to edit is non-blocking, then use the
                            -p option to pause after the program is opened.  It
                            will wait until you hit return before continuing.
    """

    version = 'v1.0'
    invocation = '# '
    enabled = True
    editor = 'suplemon'
    temp_filename = '_e_d_i_t__t_e_m_p_'

    @staticmethod
    def run(server, data):
        args = shlex.split(data, posix=False)

        pause = False
        if args[0] == '-p':
            pause = True
            args.pop(0)
        # Modify the args so that they can be passed to Popen.
        # Any more than 2 arguments and tagged filenames are
        # required.
        if len(args) > 2:
            filepaths = [fp[3:] for fp in args if fp.startswith('<f>')]
            if not filepaths:
                print('< Editing requires a filepath in order to function. >')
                return
            filepath = filepaths[0]
        # Just 2 arguments means the editor will be the first argument.
        elif len(args) == 2:
            filepath = '<f>{}'.format(args[1])
        # 1 arg means we need to open up the file with the editor
        # set in the static variable Plugin.editor.
        elif len(args) == 1:
            args.insert(0, Plugin.editor)
            filepath = '<f>{}'.format(args[1])
            args[1] = filepath
        else:
            print('< Editing requires a filepath in order to function. >')
            return

        # Remove the <f> tag from any argument, where it exists as the
        # first 3 characters, if it exists.
        untagged_filepath = filepath if filepath[:3] != '<f>' else filepath.replace('<f>', '', 1)

        # Step 1.
        # Send the file name over to the client and expect a response.
        r = server.send_command('{}{}'.format(Plugin.invocation, untagged_filepath))

        # If the client doesn't respond with "OK"
        # then there was a problem opening the file
        # so print the response.
        if r.strip() != 'OK':
            print(r)
            return

        # Step 2.
        # Receive the remote filename.
        remote_file_name = server.connection_mgr.current_connection.get_response()
        if remote_file_name[:7] == 'ERROR: ':
            print(remote_file_name)
            return

        # Create a temporary file using the remote file's extension if possible.
        extension = remote_file_name.split('.')[-1] if '.' in remote_file_name else ''
        if extension:
            temp_file_name = '{}.{}'.format(Plugin.temp_filename, extension)
        else:
            temp_file_name = Plugin.temp_filename

        # Step 3.
        # Get the file data from the client.
        file_data = server.connection_mgr.current_connection.get_response(decode=False)
        with open(temp_file_name, 'wb') as f:
            f.write(file_data)
            f.close()

        # Replace tagged file names with the temporary filename.
        args = [arg if '<f>' not in arg else temp_file_name for arg in args]

        # Open the process.
        p = Popen(args=args)
        p.communicate()
        p.terminate()

        if pause:
            safe_input('< Ready? >')

        # Open the temporary file and send the file data over to the client.
        # If the file was saved after editing, then the changes will be
        # made to the file client-side!
        with open(temp_file_name, 'rb') as f:
            new_file_data = f.read()
            # Step 4.
            # Send the new unencoded file data over to the client.
            r = server.send_command(new_file_data, encode=False)
            if r.strip() != 'OK':
                print(r)
                return

        # Remove the temporary file.
        remove(temp_file_name)
        return







