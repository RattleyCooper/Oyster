from base64 import b64decode
from uuid import uuid4
from common import bytes_packet


class ServerConnection(object):
    """
    A ServerConnection is a parent object used to customize the way data is sent to and received
    from a ClientConnection.  The methods present in the child ServerConnection object need to
    be able to interpret received data and properly format data to send via the `send_data`
    and `receive_data` methods.
    """
    def __init__(self, connection, address, recv_size=1024):
        self.connection = connection
        self.ip, self.port = address[0], address[1]
        self.recv_size = int(recv_size)
        self.status = 'OPEN'

    def close(self):
        """
        Close the connection.

        :return:
        """

        self.send_command('oyster disconnect')
        closing = True
        self.status = 'CLOSED'
        while closing:
            try:
                self.connection.close()
            except OSError as e:
                if e.errno == 9:
                    continue
            except Exception as e:
                continue
            closing = False
        return self

    def try_close(self, connection):
        """
        Try to close a connection.

        :param connection:
        :return:
        """

        closed = False
        self.status = 'CLOSED'
        try:
            connection.close()
            closed = True
        except OSError as e:
            # Bad file descriptor / writing to socket.
            if e.errno == 9:
                return True
        except Exception as e:
            return False
        return closed

    def send_command(self, command, echo=False, encode=True, file_response=False):
        """
        Send a command to the connection.

        :param command:
        :param echo:
        :param encode:
        :return:
        """

        pass

    def get_file_response(self, filepath, echo=False):
        """
        Receive a response from the server.

        :return:
        """

        pass

    def get_response(self, echo=False):
        """
        Receive a response from the server.

        :param echo:
        :return:
        """

        pass


class HeaderServer(ServerConnection):
    """
    A HeaderServer is a child of the ServerConnection object and uses headers containing
    the data's length to denote when data is finished being sent to the HeaderClient.
    """
    def __init__(self, sock, address, recv_size=1024):
        super(HeaderServer, self).__init__(sock, address, recv_size=recv_size)

    def send_command(self, command, echo=False, encode=True, file_response=False):
        """
        Send a command to the connection.

        :param command:
        :param echo:
        :param encode:
        :return:
        """

        if echo:
            print('Sending Command: {}'.format(command))

        try:
            command = command.decode('utf-8')
        except AttributeError:
            command = command

        try:
            if encode:
                command = str.encode(command)
                lp = str.encode(bytes_packet(command))
                data = lp + command
            else:
                lp = bytes_packet(str.encode(command))
                data = lp + command

            self.connection.send(data)
        except BrokenPipeError as err_msg:
            self.status = 'CLOSED'
            # print('< Client disconnected. >')
            self.try_close(self.connection)
            return False
        except OSError as err_msg:
            # Client connection is already closed.
            self.status = 'CLOSED'
            return False

        if file_response:
            print('< Getting file response. >')
            return self.get_file_response(file_response)

        return self.get_response()

    def get_file_response(self, filepath, echo=False):
        """
        Receive a response from the server.

        :return:
        """

        def print_progress_bar(_recvd, _mb, _total_bytes):
            print('< {} MB / {} MB {}% [{}] >'.format(
                int(round(_recvd / 1000 / 1000, 2)),
                _mb,
                int(round((_recvd / _total_bytes) * 100, 2)),
                '#' * int((_recvd / _total_bytes) * 20) + ' ' * (20 - int((_recvd / _total_bytes) * 20))
            ), end='\r')
            return

        r = self.get_response()
        total_bytes = int(r)
        mb = round(total_bytes / 1000 / 1000, 2)
        recvd = 0
        print('< 0 MB / {} MB 0% [                    ] >'.format(mb), end='\r')
        with open(filepath, 'wb') as f:
            while True:
                data = b''
                while True:
                    try:
                        data += self.connection.recv(1)
                    except ConnectionResetError:
                        print('< ServerConnection reset by peer. >')
                        self.status = 'CLOSED'
                        break
                    if ']' in data.decode('utf-8'):
                        break

                data_string = data.decode('utf-8')

                end_pos = data_string.index(']')
                start_data = data_string[end_pos + 1:]
                header = data_string[:end_pos]
                bytes_length = int(header)

                download_extra_byte = False
                recv_length = bytes_length
                if recv_length > self.recv_size:
                    chunks = int(recv_length / self.recv_size)
                    extra = recv_length % self.recv_size
                    if extra % 2 != 0:
                        extra -= 1
                        download_extra_byte = True
                    recv_length = chunks, extra
                else:
                    if recv_length % 2 != 0:
                        recv_length -= 1
                        download_extra_byte = True

                data_len = len(str.encode(start_data))

                try:
                    if type(recv_length) == tuple:
                        chunks, extra = recv_length
                        for i in range(chunks):
                            data = self.connection.recv(self.recv_size) # .decode('utf-8')
                            recvd += self.recv_size
                            print_progress_bar(recvd, mb, total_bytes)
                            f.write(data)
                        data = self.connection.recv(extra) # .decode('utf-8')
                        recvd += extra
                        print_progress_bar(recvd, mb, total_bytes)
                        f.write(data)
                    else:
                        data = self.connection.recv(recv_length) # .decode('utf-8')
                        recvd += recv_length
                        print_progress_bar(recvd, mb, total_bytes)
                        f.write(data)
                    if download_extra_byte:
                        data = self.connection.recv(1) # .decode('utf-8')
                        recvd += 1
                        print_progress_bar(recvd, mb, total_bytes)
                        f.write(data)

                    data_len += len(data)
                except ConnectionResetError:
                    # print('< ServerConnection reset by peer. >')
                    self.status = 'CLOSED'
                    return
                if recvd >= total_bytes:
                    print()
                    break

        return filepath

    def get_bytes_header(self):
        # Get the bytes header that will tell us how much data needs to
        # be fetched in bytes.
        data = b''
        while True:
            try:
                data += self.connection.recv(1)
            except ConnectionResetError:
                print('< ServerConnection reset by peer. >')
                self.status = 'CLOSED'
                break
            if ']' in data.decode('utf-8'):
                break

        data_string = data.decode('utf-8')

        if data == b'':
            return False

        # Pull out the number of bytes we need to receive.
        end_pos = data_string.index(']')
        start_data = data_string[end_pos + 1:]
        header = data_string[:end_pos]
        return int(header), start_data

    def chunkify_bytes(self, bytes_length):
        """
        Break up the amount of bytes that should be received into chunks if needed.

        :param bytes_length:
        :return:
        """

        # Figure out how much total data needs to be received.
        download_extra_byte = False
        recv_length = bytes_length
        if recv_length > self.recv_size:
            chunks = int(recv_length / self.recv_size)
            extra = recv_length % self.recv_size
            if extra % 2 != 0:
                extra -= 1
                download_extra_byte = True
            recv_length = chunks, extra
        else:
            if recv_length % 2 != 0:
                recv_length -= 1
                download_extra_byte = True

        return recv_length, download_extra_byte

    def _get_response_receive(self, recv_length, download_extra_byte):
        # Receive the exact amount of bytes needed!
        data = b''
        try:
            if type(recv_length) == tuple:
                chunks, extra = recv_length
                for i in range(chunks):
                    data += self.connection.recv(self.recv_size)
                data += self.connection.recv(extra)
            else:
                data += self.connection.recv(recv_length)

            if download_extra_byte:
                data += self.connection.recv(1)

        except ConnectionResetError:
            # print('< ServerConnection reset by peer. >')
            self.status = 'CLOSED'
            return

        return data

    def get_response(self, echo=False):
        """
        Receive a response from the server.

        :param echo:
        :return:
        """

        header_tuple = self.get_bytes_header()
        if not header_tuple:
            return ''
        bytes_length, start_data = header_tuple
        recv_length, download_extra_byte = self.chunkify_bytes(bytes_length)
        data = self._get_response_receive(recv_length, download_extra_byte)

        # Format final output and return it
        output = str.encode(start_data) + data if type(data) == bytes else str.encode(data)
        if echo:
            print('< Response: {} >'.format(output))
        output = output.decode('utf-8')
        return output


class TerminatingServer(ServerConnection):
    """
    A TerminatingServer is a child of the ServerConnection object and uses termination strings
    to denote when data is finished being sent to the TerminatingClient.
    """
    def __init__(self, connection, address, recv_size=1024):
        super(TerminatingServer, self).__init__(connection, address, recv_size=recv_size)

    def send_command(self, command, echo=False, encode=True, file_response=False):
        """
        Send a command to the connection.

        :param command:
        :param echo:
        :param encode:
        :param file_response:
        :return:
        """

        if echo:
            print('Sending Command: {}'.format(command))
        try:
            if encode:
                self.connection.send(str.encode(command + '~!_TERM_$~'))
            else:
                self.connection.send(command)
                self.connection.send(str.encode('~!_TERM_$~'))
        except BrokenPipeError as err_msg:
            self.status = 'CLOSED'
            # print('< Client disconnected. >')
            self.try_close(self.connection)
            return False
        except OSError as err_msg:
            # Client connection is already closed.
            self.status = 'CLOSED'
            return False

        if file_response:
            print('< Getting file response. >')
            return self.get_file_response(file_response)

        return self.get_response()

    def get_file_response(self, filepath, echo=False):
        """
        Receive a response from the server.

        :return:
        """

        data_package = ''
        with open(filepath, 'wb') as f:
            while True:
                try:
                    data = self.connection.recv(self.recv_size)
                except ConnectionResetError:
                    # print('< ServerConnection reset by peer. >')
                    self.status = 'CLOSED'
                    break
                if len(data) < 1:
                    continue
                d = data.decode('utf-8')

                tstring = d[-10:]
                if tstring == '~!_TERM_$~':
                    d = d[:-10]

                if d[:9] == '[Errno 2]':
                    return d

                # Write the data!
                _ = b64decode(d)
                f.write(_)

                # Make sure the data package persists with some old data
                data_package = data_package + d + tstring if len(data_package) < 1 else data_package[-15:] + d + tstring
                # print('Data:', repr(d))
                if data_package[-10:] == '~!_TERM_$~':
                    # print('Got termination string!')
                    break

        return filepath

    def get_response(self, echo=False):
        """
        Receive a response from the server.

        :param echo:
        :return:
        """

        data_package = ''
        while True:
            try:
                data = self.connection.recv(self.recv_size)
            except ConnectionResetError:
                # print('< ServerConnection reset by peer. >')
                self.status = 'CLOSED'
                break
            if len(data) < 1:
                continue
            d = data.decode('utf-8')
            data_package += d
            # print('Data:', repr(d))
            if data_package[-10:] == '~!_TERM_$~':
                # print('Got termination string!')
                break

        data_package = data_package[:-10]
        if echo:
            print('< Response: {} >'.format(data_package))
        return data_package


class ConnectionManager(object):
    """
    Manage the ServerConnection objects added to it.
    """

    def __init__(self, connection_type):
        self.connections = {}
        self.session_id = uuid4()
        self.current_connection = None
        self.cwd = None
        self.connection_type = connection_type

    def __iter__(self):
        """
        Return an generator.

        :return:
        """

        try:
            for k, v in self.connections.iteritems():
                yield k, v
        except:
            for k, v in self.connections.items():
                yield k, v

    def __len__(self):
        """
        Return the amount of connections in the pool.

        :return:
        """

        return len(self.connections)

    def __getitem__(self, item):
        """
        Get item from dictionary by key or by index.

        :param item:
        :return:
        """

        if str(item).isdigit():
            return list(self.connections.values())[int(item)]
        return self.connections[item]

    def __setitem__(self, key, value):
        """
        Set an item in the dictionary.

        :param key:
        :param value:
        :return:
        """

        self.connections[key] = value

    def __delitem__(self, key):
        """
        Delete item connection from pool.

        :param key:
        :return:
        """

        self.connections.pop(key)

    def __str__(self):
        """
        Print out the client data.

        :return:
        """

        c = 0
        client_data = "-------------- Clients --------------\n"
        for key, connection in self.connections.items():
            client_data += '[{}]'.format(c) + '   ' + key + '   ' + str(connection.port) + '\n'
            c += 1
        return client_data

    def close(self):
        """
        Close a the current connection.

        :return:
        """

        if self.current_connection is not None:
            self.current_connection.close()
        return self

    def use_connection(self, ip):
        """
        Use the given IP as the current connection.  An index can be passed as well.

        :param ip:
        :return:
        """

        if ip is None:
            self.current_connection = None
            return None

        # Set the use_index variable based on whether or not we can int() it the ip.
        try:
            int(ip)
            use_index = True
        except ValueError:
            use_index = False

        # If we need to use_index, then look up the dictionary entry by index.
        # If not, do regular dictionary lookup.
        if use_index:
            try:
                self.current_connection = list(self.connections.values())[int(ip)]
            except (KeyError, IndexError):
                print('< No connection for the given key/index. >')
                return None
        else:
            try:
                self.current_connection = self.connections[str(ip)]
            except KeyError:
                print('< No connection for the given IP address. >')
                return None
        return self.current_connection

    def remove_connection(self, connection):
        """
        Remove a connection.

        :param connection:
        :return:
        """

        ip = False
        for _ip, conn in self.connections.items():
            if conn == connection:
                ip = _ip
                break
        if ip:
            # print('< Removing connection - {} >'.format(ip))
            self.connections.pop(ip)
        return self

    def send_command(self, command, echo=False, encode=True, file_response=False):
        """
        Send a command to the currently selected client.

        :param command:
        :param echo:
        :param encode:
        :param file_response:
        :return:
        """

        if self.current_connection and self.current_connection.status == 'CLOSED':
            self.close_connection(self.current_connection.ip)
            self.remove_connection(self.current_connection)
            self.current_connection = None
            return ''

        if self.current_connection is None:
            print('< Run the `use` command to select a connection by ip address before sending commands. >')
            return ''

        try:
            response = self.current_connection.send_command(command, encode=encode, file_response=file_response)
        except BrokenPipeError as err_msg:
            self.current_connection = None
            return ''

        if echo:
            print(response)
        return response

    def send_commands(self, command, echo=False):
        """
        Send a command to all of the clients.

        :param command:
        :param echo:
        :return:
        """

        response = ''
        for ip, connection in self.connections.items():
            self.current_connection = connection
            if self.current_connection.status == 'CLOSED':
                self.close_connection(self.current_connection.ip)
                self.remove_connection(self.current_connection)
                self.current_connection = None
                continue
            response += connection.send_command(command)

        self.current_connection = None
        if echo:
            print(response)
        return response

    def close_all_connections(self):
        """
        Close all the connections in the pool.

        :return:
        """

        for key, connection in self.connections.items():
            self.close_connection(key)

        self.connections = {}
        return self

    def close_connection(self, ip_address):
        """
        Close and remove a connection from the connection pool.

        :param ip_address:
        :return:
        """

        print('< Closing connection - {} >'.format(ip_address))
        self.connections[ip_address].close()
        return self

    def server_should_shutdown(self, address):
        """
        Check to see if the given address connected with a shutdown command for the server.

        :param address:
        :return:
        """

        return True if self.connections[address].send_command('oyster server_shutdown?') == 'Y' else False

    def add_connection(self, connection, address):
        """
        Add a connection to the connection pool.

        :param connection:
        :param address:
        :return:
        """

        self.connections[str(address[0])] = self.connection_type(connection, address)
        # conn.send_command('oyster set-session-id {}'.format(self.session_id))
        return self
