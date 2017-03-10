import shlex
try:
    from importlib import reload
except ImportError:
    pass


class Plugin(object):
    version = 'v1.0'
    invocation = 'plugins'
    enabled = True

    def run(self, server, data):
        args = shlex.split(data)

        if args[0] == '-l':
            self.list_plugins(server)
        if args[0] == '-ls':
            self.list_server_plugins(server)
        if args[0] == '-lsh':
            self.list_shell_plugins(server)
        if args[0] == '-r':
            self.reload_plugins(server)

    def reload_plugins(self, server):
        """
        Reload all of the server-side plugins

        :param server:
        :return:
        """

        print('Reloading Plugins...')
        shell_plugins = server.get_shell_plugins()
        server_plugins = server.get_server_plugins()

        plugins = server_plugins + shell_plugins

        for plugin in plugins:
            reload(plugin)
        print('Plugins Reloaded...')
        return

    def list_server_plugins(self, server):
        """
        List server plugins installed on the system

        :param server:
        :return:
        """

        plugins = server.get_server_plugins()

        enabled = [
            '   [enabled]    {} - {}'.format(
                pn.__name__.replace('server_plugins.', ''),
                pn.Plugin.invocation
            )
            for pn in plugins
            if pn.Plugin.enabled
            ]

        disabled = [
            '   [disabled]   {} - {}'.format(
                pn.__name__.replace('server_plugins.', ''),
                pn.Plugin.invocation
            )
            for pn in plugins
            if not pn.Plugin.enabled
            ]

        output = ['\n< Server Plugins >'] + enabled + disabled + ['< /Server Plugins >']
        print('\n\n'.join(output) + '\n')
        return

    def list_shell_plugins(self, server):
        """
        List the installed shell plugins

        :param server:
        :return:
        """

        plugins = server.get_shell_plugins()

        enabled = [
            '   [enabled]    {} - {}'.format(
                pn.__name__.replace('shell_plugins.', ''),
                pn.Plugin.invocation
            )
            for pn in plugins
            if pn.Plugin.enabled
        ]

        disabled = [
            '   [disabled]   {} - {}'.format(
                pn.__name__.replace('shell_plugins.', ''),
                pn.Plugin.invocation
            )
            for pn in plugins
            if not pn.Plugin.enabled
        ]

        output = ['\n< Shell Plugins >'] + enabled + disabled + ['< /Shell Plugins >']
        output_str = '\n\n'.join(output) + '\n'
        print(output_str)
        return

    def list_plugins(self, server):
        """
        List all plugins installed server-side

        :param server:
        :return:
        """

        self.list_shell_plugins(server)
        self.list_server_plugins(server)
        return

