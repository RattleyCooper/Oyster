import shlex
import os
from shutil import copy


class Plugin(object):
    version = 'v0.1'
    invocation = 'client '
    enabled = True

    def run(self, server, data):
        args = shlex.split(data)

        if not args:
            print('Help doc coming soon.')
            return

        if args[0] == '-b':
            try:
                return Plugin.dispatch_batch_command(server, ' '.join(args[1:]))
            except IndexError:
                print('< You must include a command to send. >')
                return

        if args[0] == '-d':
            Plugin.handle_dist_flag()
            return

    @staticmethod
    def dispatch_batch_command(server, command):
        """
        Send the command given after the -a flag to all connected clients.

        :param server:
        :param command:
        :return:
        """

        if not command:
            print('< You must include a command. >')
            return ''
        response = server.connection_mgr.send_commands(command)
        print(response, end='')
        return response

    @staticmethod
    def handle_dist_flag():
        """
        Copy the client-specific files into the "dist" folder.

        :return:
        """

        oyster_fp = __file__.replace('shell_plugins/', '').replace(__file__.split('/')[-1], '')
        client_plugins_filepath = oyster_fp + 'client_plugins/'

        client_plugin_filenames = [n for n in os.listdir(client_plugins_filepath)]
        hidden_files = [n for n in os.listdir(client_plugins_filepath) if n[0] == '.']
        client_plugin_filenames = [n for n in client_plugin_filenames if n not in hidden_files]

        print('\r< Creating client distribution package... >')
        try:
            os.mkdir(oyster_fp + 'dist')
            os.mkdir(oyster_fp + 'dist/client_plugins')
        except FileExistsError:
            pass

        for filename in client_plugin_filenames:
            destination = oyster_fp + 'dist/client_plugins/' + filename
            origin = client_plugins_filepath + filename
            copy(origin, destination)

        copy(oyster_fp + '__init__.py', oyster_fp + 'dist/__init__.py')
        copy(oyster_fp + 'common.py', oyster_fp + 'dist/common.py')
        copy(oyster_fp + 'client.py', oyster_fp + 'dist/client.py')
        copy(oyster_fp + 'update.py', oyster_fp + 'dist/update.py')

        print('\r< Finished... >')
        return


if __name__ == '__main__':
    p = Plugin()
    p.run('', '-d')
