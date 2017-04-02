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

    Example:

        Oyster> use 0
        <127.0.0.1> /Some/Dir/Oyster> plugins -r
        < 7 Client Plugins Reloaded. >
        Oyster>
    """

    version = 'v1.0'
    invocation = 'plugins'
    enabled = True

    @staticmethod
    def run(client, data):
        """
        Main entry point for handling/parsing the command.

        :param client:
        :param data:
        :return:
        """

        args = shlex.split(data)

        help_info = "Use `plugins -r` to reload plugins and `plugins -l` to list plugins.\n"

        if not args:
            client.send_data(help_info)
            return

        help_commands = ['-h', '-help', '--help', 'help']
        if args[0].lower() in help_commands:
            client.send_data(help_info)
            return

        if args[0].lower() == '-r':
            Plugin.reload_plugins(client)
            return

        if args[0].lower() == '-l':
            Plugin.list_plugins(client)
            return

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
        Get a list of strings for the enabled plugins.

        :param plugins:
        :return list:
        """

        return Plugin.plugins_strings(plugins)

    @staticmethod
    def disabled_plugins_strings(plugins):
        """
        Get a list of strings for the disabled plugins.

        :param plugins:
        :return list:
        """

        return Plugin.plugins_strings(plugins, enabled=False)

    @staticmethod
    def list_plugins(client):
        """
        Send a list of plugins back to the server

        :param client:
        :return:
        """

        plugins = client.get_client_plugins()

        enabled = Plugin.enabled_plugins_strings(plugins)
        disabled = Plugin.disabled_plugins_strings(plugins)

        output = ['\n< Client Plugins >'] + enabled + disabled + ['< /Client Plugins >']

        client.send_data('\n\n'.join(output) + '\n\n')
        return

    @staticmethod
    def reload_plugins(client):
        """
        Reload the client-side plugins

        :param client:
        :return:
        """

        print('< Reloading Plugins. >')
        client_plugins = client.get_client_plugins()

        for plugin in client_plugins:
            reload(plugin)
        print('< Plugins Reloaded. >')
        client.send_data('< {} Client Plugins Reloaded. >\n'.format(len(client_plugins)))
        return
