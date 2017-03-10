try:
    from importlib import reload
except:
    pass


class Plugin(object):
    """
    Reload the client plugins
    """

    version = 'v1.0'
    invocation = 'reload-plugins'
    enabled = True

    def run(self, client, data):
        print('Reloading Plugins...')
        client_plugins = client.get_client_plugins()

        for plugin in client_plugins:
            reload(plugin)
        print('Plugins Reloaded...')
        client.send_data('Client Plugins Reloaded...\n')



