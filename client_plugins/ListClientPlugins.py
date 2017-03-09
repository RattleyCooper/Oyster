from os import listdir


class Plugin(object):
    version = 'v1.0'
    invocation = 'client-plugins'

    def run(self, client, data):
        fp = __file__.replace('ListClientPlugins.py', '').replace('ListClientPlugins.pyc', '')
        module_names = [n.replace('.py', '').replace('.pyc', '') for n in listdir(fp) if '__' not in n]
        module_names.insert(0, '\n< Client Plugins >')
        client.send_data('\n'.join(module_names) + '\n\n')
        return
