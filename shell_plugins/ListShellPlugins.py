

class Plugin(object):
    """
    Get a list of the shell plugins and print them
    """

    version = 'v1.0'
    invocation = 'shell-plugins'
    enabled = True

    def run(self, server, data):
        plugins = server.get_shell_plugins()

        enabled = [
            '{} - enabled'.format(
                pn.__name__.replace('shell_plugins.', '')
            )
            for pn in plugins
            if pn.Plugin.enabled
        ]

        disabled = [
            '{} - disabled'.format(
                pn.__name__.replace('shell_plugins.', '')
            )
            for pn in plugins
            if not pn.Plugin.enabled
        ]

        output = ['\n< Shell Plugins >'] + enabled + disabled

        print('\n'.join(output) + '\n')
        return


