try:
    from importlib import reload
except:
    pass


class Plugin(object):
    invocation = 'reload-plugins'

    def run(self, client, data):
        print('Reloading Plugins...')
        client_plugins = client.get_client_plugins()

        for plugin in client_plugins:
            reload(plugin)
        print('Plugins Reloaded...')
        client.send_data('Client Plugins Reloaded...\n')



