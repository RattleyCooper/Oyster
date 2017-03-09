try:
    from importlib import reload
except:
    pass


class Plugin(object):
    invocation = 'reload-plugins'

    def run(self, server, data):
        print('Reloading Plugins...')
        shell_plugins = server.get_shell_plugins()
        server_plugins = server.get_server_plugins()

        plugins = server_plugins + shell_plugins

        for plugin in plugins:
            reload(plugin)
        print('Plugins Reloaded...')


