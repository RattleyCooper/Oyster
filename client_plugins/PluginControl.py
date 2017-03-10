import shlex
try:
    from importlib import reload
except ImportError:
    pass


class Plugin(object):
    """
    Handles all of the `plugins` commands

    plugins -r          -       Reload all plugins.
    plugins -l          -       List all plugins.
    """

    version = 'v1.0'
    invocation = 'plugins'
    enabled = True

    def run(self, client, data):
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
            self.reload_plugins(client)
            return

        if args[0].lower() == '-l':
            self.list_plugins(client)
            return

        return

    def list_plugins(self, client):
        """
        Send a list of plugins back to the server

        :param client:
        :return:
        """

        plugins = client.get_client_plugins()

        enabled = [
            '   [enabled]    {} {} - {}'.format(
                pn.__name__.replace('client_plugins.', ''),
                pn.Plugin.version,
                pn.Plugin.invocation
            )
            for pn in plugins
            if pn.Plugin.enabled
            ]

        disabled = [
            '   [disabled]   {} {} - {}'.format(
                pn.__name__.replace('client_plugins.', ''),
                pn.Plugin.version,
                pn.Plugin.invocation
            )
            for pn in plugins
            if not pn.Plugin.enabled
            ]

        output = ['\n< Client Plugins >'] + enabled + disabled + ['< /Client Plugins >']

        client.send_data('\n\n'.join(output) + '\n\n')
        return

    def reload_plugins(self, client):
        """
        Reload the client-side plugins

        :param client:
        :return:
        """

        print('Reloading Plugins...')
        client_plugins = client.get_client_plugins()

        for plugin in client_plugins:
            reload(plugin)
        print('Plugins Reloaded...')
        client.send_data('Client Plugins Reloaded...\n')
        return
