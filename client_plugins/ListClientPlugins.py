from os import listdir


class Plugin(object):
    version = 'v1.0'
    invocation = 'cplug list'

    def run(self, client, data):
        fp = __file__.replace('ListClientPlugins.py', '').replace('ListClientPlugins.pyc', '')
        module_names = [n.replace('.py', '').replace('.pyc', '') for n in listdir(fp) if '__' not in n]
        client.send_data('\n'.join(module_names) + '\n')
        return
