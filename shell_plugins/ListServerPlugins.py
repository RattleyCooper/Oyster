from os import listdir


class Plugin(object):
    version = 'v1.0'
    invocation = 'server-plugins'

    def run(self, server, data):
        fp = __file__.replace('ListServerPlugins.py', '').replace('ListServerPlugins.pyc', '').replace('shell_plugins', 'server_plugins')
        module_names = [n.replace('.py', '').replace('.pyc', '') for n in listdir(fp) if '__' not in n]
        module_names.insert(0, '\n< Server Plugins >')
        print('\n'.join(module_names) + '\n')
        return


