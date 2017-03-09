from os import listdir


class Plugin(object):
    version = 'v1.0'
    invocation = 'shell-plugins'

    def run(self, client, data):
        fp = __file__.replace('ListShellPlugins.py', '').replace('ListShellPlugins.pyc', '')
        module_names = [n.replace('.py', '').replace('.pyc', '') for n in listdir(fp) if '__' not in n]
        module_names.insert(0, '\n< Shell Plugins >')
        print('\n'.join(module_names) + '\n')
        return


