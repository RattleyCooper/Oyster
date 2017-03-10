try:
    from importlib import reload
except:
    pass


class Plugin(object):
    """
    Reload the shell/server plugins
    """

    version = 'v1.0'
    invocation = 'reload-plugins'
    enabled = True

    def run(self, server, data):
        print('Reloading Plugins...')
        shell_plugins = server.get_shell_plugins()
        server_plugins = server.get_server_plugins()

        plugins = server_plugins + shell_plugins

        for plugin in plugins:
            reload(plugin)
        print('Plugins Reloaded...')


