import shlex
try:
    from importlib import reload
except ImportError:
    pass


class Plugin(object):
    """
    PluginControl v1.0

    Reload & list installed plugins.

    Invocation:

        plugins

    Commands:

        plugins -r          -   Reload the installed plugins.
        plugins -l          -   List the installed plugins.
        plugins -lo         -   List the installed outgoing plugins.
        plugins -ls         -   List the installed shell plugins.

    Example:

        Oyster> plugins -r
        < Reloading Plugins. >
        < 12 Plugins Reloaded. >
        Oyster>
    """

    version = 'v1.0'
    invocation = 'plugins'
    enabled = True

    @staticmethod
    def run(server, data):
        """
        Main entry point for handling/parsing the command.

        :param server:
        :param data:
        :return:
        """

        args = shlex.split(data)

        if args[0] == '-l':
            print(Plugin.list_plugins(server))
        if args[0] == '-lo':
            print(Plugin.list_outgoing_plugins(server))
        if args[0] == '-ls':
            print(Plugin.list_shell_plugins(server))
        if args[0] == '-r':
            Plugin.reload_plugins(server)

    @staticmethod
    def reload_plugins(server):
        """
        Reload all of the server-side plugin files

        :param server:
        :return:
        """

        print('< Reloading Plugins. >')
        shell_plugins = server.get_shell_plugins()
        outgoing_plugins = server.get_outgoing_plugins()

        server.outgoing_plugins = outgoing_plugins
        server.shell_plugins = shell_plugins

        plugins = outgoing_plugins + shell_plugins

        for plugin in plugins:
            reload(plugin)
        print('< {} Plugins Reloaded. >'.format(len(plugins)))
        return

    @staticmethod
    def plugins_strings(plugins, enabled=True):
        """
        Get a list of strings for enabled or disabled plugins.

        :param plugins:
        :param enabled:
        :return list:
        """

        output = []
        for plugin in plugins:
            if not plugin.Plugin.enabled:
                continue
            plugin_string = '   [{}]   < {} {} >'.format(
                    'enabled' if enabled else 'disabled',
                    plugin.__name__.replace('outgoing_plugins.', ''),
                    plugin.Plugin.version
                )
            plugin_string += '\n     invocation: {}'.format(
                    plugin.Plugin.invocation
                )
            output.append(plugin_string)
        return output

    @staticmethod
    def enabled_plugins_strings(plugins):
        """
        Get a list of strings for the enabled plugins in the given list of plugins.

        :param plugins:
        :return list:
        """

        return Plugin.plugins_strings(plugins)

    @staticmethod
    def disabled_plugins_strings(plugins):
        """
        Get a list of strings for the disabled plugins in the given list of plugins.

        :param plugins:
        :return list:
        """

        return Plugin.plugins_strings(plugins, enabled=False)

    @staticmethod
    def list_outgoing_plugins(server):
        """
        Get a string listing the outgoing plugins installed on the system

        :param server:
        :return str output:
        """

        plugins = server.get_outgoing_plugins()

        enabled = Plugin.enabled_plugins_strings(plugins)
        disabled = Plugin.disabled_plugins_strings(plugins)

        output = ['\n< Outgoing Plugins >'] + enabled + disabled + ['< /Outgoing Plugins >']
        output = '\n\n'.join(output) + '\n'

        return output

    @staticmethod
    def list_shell_plugins(server):
        """
        Get a string listing the installed shell plugins

        :param server:
        :return str output:
        """

        plugins = server.get_shell_plugins()

        enabled = Plugin.enabled_plugins_strings(plugins)
        disabled = Plugin.disabled_plugins_strings(plugins)

        output = ['\n< Shell Plugins >'] + enabled + disabled + ['< /Shell Plugins >']
        output = '\n\n'.join(output) + '\n'

        return output

    @staticmethod
    def list_plugins(server):
        """
        List all plugins installed server-side

        :param server:
        :return:
        """

        return Plugin.list_outgoing_plugins(server) + Plugin.list_shell_plugins(server)


if __name__ == '__main__':
    help(Plugin)

