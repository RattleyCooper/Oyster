from time import sleep


class Plugin(object):
    version = 'v1.0'
    invocation = 'update '
    enabled = True

    def run(self, client, data):
        print('Overwriting client...')
        with open('client.py', 'w') as f:
            f.write(data)
            f.close()
        client.send_data('Client updated...\n')
        print('Rebooting in 2 seconds...')
        sleep(2)
        print('###################### REBOOTING ######################')
        client.reboot_self()
        return
