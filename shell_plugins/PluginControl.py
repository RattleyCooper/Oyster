import shlex
try:
    from importlib import reload
except ImportError:
    pass


class Plugin(object):
    version = 'v1.0'
    invocation = 'plugins'
    enabled = True

    @staticmethod
    def run(server, data):
        args = shlex.split(data)

        if args[0] == '-l':
            Plugin.list_plugins(server)
        if args[0] == '-ls':
            Plugin.list_server_plugins(server)
        if args[0] == '-lsh':
            Plugin.list_shell_plugins(server)
        if args[0] == '-r':
            Plugin.reload_plugins(server)

    @staticmethod
    def reload_plugins(server):
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

    @staticmethod
    def enabled_plugins_string(plugins):
        return [
            '   [enabled]    {} {} - {}'.format(
                pn.__name__.replace('server_plugins.', ''),
                pn.Plugin.version,
                pn.Plugin.invocation
            )
            for pn in plugins
            if pn.Plugin.enabled
            ]

    @staticmethod
    def disabled_plugins_string(plugins):
        return [
            '   [disabled]   {} {} - {}'.format(
                pn.__name__.replace('server_plugins.', ''),
                pn.Plugin.version,
                pn.Plugin.invocation
            )
            for pn in plugins
            if not pn.Plugin.enabled
            ]

    @staticmethod
    def list_server_plugins(server):
        """
        List server plugins installed on the system

        :param server:
        :return:
        """

        plugins = server.get_server_plugins()

        enabled = Plugin.enabled_plugins_string(plugins)
        disabled = Plugin.disabled_plugins_string(plugins)

        output = ['\n< Server Plugins >'] + enabled + disabled + ['< /Server Plugins >']
        print('\n\n'.join(output) + '\n')
        return

    @staticmethod
    def list_shell_plugins(server):
        """
        List the installed shell plugins

        :param server:
        :return:
        """

        plugins = server.get_shell_plugins()

        enabled = Plugin.enabled_plugins_string(plugins)
        disabled = Plugin.disabled_plugins_string(plugins)

        output = ['\n< Shell Plugins >'] + enabled + disabled + ['< /Shell Plugins >']
        output_str = '\n\n'.join(output) + '\n'
        print(output_str)
        return

    @staticmethod
    def list_plugins(server):
        """
        List all plugins installed server-side

        :param server:
        :return:
        """

        Plugin.list_server_plugins(server)
        Plugin.list_shell_plugins(server)
        return

