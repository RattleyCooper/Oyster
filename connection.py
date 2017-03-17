from base64 import b64decode
from uuid import uuid4


class Connection(object):
    """
    Manages a socket object.
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
                    # print('< Connection reset by peer. >')
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

        :return:
        """

        data_package = ''
        while True:
            try:
                data = self.connection.recv(self.recv_size)
            except ConnectionResetError:
                print('< Connection reset by peer. >')
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
    Manage the Connection objects added to it.
    """

    def __init__(self):
        self.connections = {}
        self.session_id = uuid4()
        self.current_connection = None
        self.cwd = None

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
        :return:
        """

        if self.current_connection.status == 'CLOSED':
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
            return

        if echo:
            print(response)
        self.cwd = self.current_connection.send_command('oyster getcwd')
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

        self.connections[str(address[0])] = Connection(connection, address)
        # conn.send_command('oyster set-session-id {}'.format(self.session_id))
        return self
