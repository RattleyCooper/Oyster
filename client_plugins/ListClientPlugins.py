from os import listdir


class Plugin(object):
    """
    Send a list of the client plugins back to the server
    """

    version = 'v1.0'
    invocation = 'client-plugins'
    enabled = True

    def run(self, client, data):
        plugins = client.get_client_plugins()

        enabled = [
            '{} - enabled'.format(
                pn.__name__.replace('client_plugins.', '')
            )
            for pn in plugins
            if pn.Plugin.enabled
            ]

        disabled = [
            '{} - disabled'.format(
                pn.__name__.replace('client_plugins.', '')
            )
            for pn in plugins
            if not pn.Plugin.enabled
            ]

        output = ['\n< Client Plugins >'] + enabled + disabled

        client.send_data('\n'.join(output) + '\n\n')
        return
