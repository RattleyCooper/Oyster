from os import listdir


class Plugin(object):
    """
    Get a list of the server plugins and print them
    """

    version = 'v1.0'
    invocation = 'server-plugins'
    enabled = True

    def run(self, server, data):
        plugins = server.get_server_plugins()

        enabled = [
            '{} - enabled'.format(
                pn.__name__.replace('server_plugins.', '')
            )
            for pn in plugins
            if pn.Plugin.enabled
            ]

        disabled = [
            '{} - disabled'.format(
                pn.__name__.replace('server_plugins.', '')
            )
            for pn in plugins
            if not pn.Plugin.enabled
            ]

        output = ['\n< Server Plugins >'] + enabled + disabled
        print('\n'.join(output) + '\n')
        return


