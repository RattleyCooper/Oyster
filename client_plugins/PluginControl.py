import shlex
try:
    from importlib import reload
except ImportError:
    pass


class Plugin(object):
    version = 'v1.0'
    invocation = 'plugins'
    enabled = True

    def run(self, client, data):
        args = shlex.split(data)

        if args[0].lower() == '-r':
            self.reload_plugins(client)

        if args[0].lower() == '-l':
            self.list_plugins(client)

        return

    def list_plugins(self, client):
        """
        Send a list of plugins back to the server

        :param client:
        :return:
        """

        plugins = client.get_client_plugins()

        enabled = [
            '   [enabled]    {} - {}'.format(
                pn.__name__.replace('client_plugins.', ''),
                pn.Plugin.invocation
            )
            for pn in plugins
            if pn.Plugin.enabled
            ]

        disabled = [
            '   [disabled]   {} - {}'.format(
                pn.__name__.replace('client_plugins.', ''),
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
