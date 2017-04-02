import sys
from base64 import b64decode
from uuid import uuid4
from time import sleep
from common import bytes_packet
import socket


class ClientConnection(object):
    """
    A ClientConnection is a parent object used to customize the way data is sent to and received
    from a ServerConnection.  The methods present in the child ClientConnection object need to
    be able to interpret received data and properly format data to send via the `send_data`
    and `receive_data` methods.
    """
    def __init__(self, host='', port=6667, recv_size=1024, session_id='', echo=True):
        self.host = host
        self.port = port
        self.recv_size = recv_size
        self.session_id = session_id
        self.echo = echo
        self.reconnect_to_session = True
        self.ip_address = '0.0.0.0'
        self.connected_port = '00000'
        self.__file__ = sys.argv[0]
        self.connected = False
        self.sock = self.connect_to_server()
        self.connection = self.sock

    def connect_to_server(self):
        """
        Ping the control server until it accepts the connection.

        :return:
        """

        self.sock = False
        self.connected = False

        # Loop until the connection is successful.
        while True:
            self.sock = socket.socket()
            self.sock.setblocking(True)
            try:
                self.sock.connect((self.host, self.port))
                if self.echo:
                    print('< Connected to server. >')
                break
            except socket.error as the_error_message:
                if self.echo:
                    print('< Waiting for control server {}:{} {} >'.format(self.host, self.port, the_error_message))
                sleep(5)

        return self.sock

    def send_data(self, some_data, echo=True, encode=True, chunks=False):
        """
        Send data to the server.

        If using a termination string, you need to send that with the data.
        If using headers to denote the length of the data, then you need
        to include that when you send the data over to the server.

        :param some_data:
        :param echo:
        :param encode:
        :param chunks:
        :return:
        """

        pass

    def receive_data(self, echo=False, decode=True):
        """
        Receive data from the server until we get the termination string or the amount of
        data specified in the header.

        :param echo:
        :param decode:
        :return:
        """

        pass

    def terminate(self):
        """
        If the server expects a response but there is no data to send, call this method to
        send a response of some sort.

        If using a terminating string then the terminating string should be sent back to
        the server.  If using headers to denote the length of the data, you should be
        able to send a blank string since the `send_data` method should craft the
        header and send it over automatically with the data.

        :return:
        """
        pass

    def set_session_id(self, session_id):
        """
        Set the session id for the client.

        :param session_id:
        :return:
        """

        self.session_id = session_id
        return self


class TerminatingClient(ClientConnection):
    """
    A TerminatingClient is a child of the ClientConnection object and uses termination strings
    to denote when data is finished being sent to the TerminatingServer.
    """
    def __init__(self, host='', port=6667, recv_size=1024, session_id='', echo=True):
        super(TerminatingClient, self).__init__(
            host=host,
            port=port,
            recv_size=recv_size,
            session_id=session_id,
            echo=echo
        )

    def __getattr__(self, item):
        """
        If the object is missing an attribute, check the `sock` attribute to see if it has it.
        This is to support backwards compatibility with plugins that may use

        :param item:
        :return:
        """
        attr = False
        try:
            attr = object.__getattribute__(self, item)
            base_obj_missing_attr = False
        except AttributeError:
            base_obj_missing_attr = True

        if base_obj_missing_attr and hasattr(self.sock, item):
            return getattr(self.sock, item)
        else:
            try:
                return attr
            except AttributeError:
                raise AttributeError("{} is not set as an attribute.".format(item))

    def send_data(self, some_data, echo=True, encode=True, chunks=False):
        if echo:
            if self.echo:
                print('< Sending Data:', some_data, '>')

        if encode:
            self.sock.send(str.encode(str(some_data)))
        else:
            self.sock.send(some_data)

        if not chunks:
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
        if self.echo:
            print('< Receiving data. >')
        while accepting:
            try:
                data = self.sock.recv(self.recv_size)
            except socket.error as error_message:
                if self.echo:
                    print('Server closed connection:', error_message)
                self.sock.close()
                self.sock = self.connect_to_server()
                continue

            # Continue looping if there is no data.
            if len(data) < 1:
                if self.echo:
                    print('< Zero data received. >', end='\r')
                self.sock.close()
                self.sock = self.connect_to_server()
                continue

            # Decode from bytes.
            d = data.decode('utf-8')

            total_data += d
            if echo:
                if self.echo:
                    print('Data:', d)

            # Check for termination string.
            if total_data[-10:] == '~!_TERM_$~':
                accepting = False

        if echo:
            if self.echo:
                print('Data received: {}'.format(total_data[:-10]))

        # Chop off the termination string from the total data and assign it to data.
        # Data should now be a string as well.
        data = total_data[:-10]
        return data

    def terminate(self):
        self.send_data('~!_TERM_$~', chunks=True)


class HeaderClient(ClientConnection):
    """
    A HeaderClient is a child of the ClientConnection object and uses headers containing
    the data's length to denote when data is finished being sent to the HeaderServer.
    """
    def __init__(self, host='', port=6667, recv_size=1024, session_id='', echo=True):
        super(HeaderClient, self).__init__(
            host=host,
            port=port,
            recv_size=recv_size,
            session_id=session_id,
            echo=echo
        )

    def __getattr__(self, item):
        attr = False
        try:
            attr = object.__getattribute__(self, item)
            base_obj_missing_attr = False
        except AttributeError:
            base_obj_missing_attr = True

        if base_obj_missing_attr and hasattr(self.sock, item):
            return getattr(self.sock, item)
        else:
            try:
                return attr
            except AttributeError:
                raise AttributeError("{} is not set as an attribute.".format(item))

    def send_data(self, some_data, echo=True, encode=True, chunks=False):
        """
        Send data to the server.

        :param some_data:
        :param echo:
        :param encode:
        :param chunks:
        :return:
        """

        try:
            if encode:
                some_data = some_data.decode('utf-8')
        except (AttributeError, UnicodeDecodeError):
            some_data = some_data

        if echo:
            if self.echo:
                print('< Sending Data:', some_data, '>')

        if encode:
            some_data = str.encode(some_data)
            lp = str.encode(bytes_packet(some_data))
            data = lp + some_data
        else:
            if type(some_data) == str:
                some_data = str.encode(some_data)
            data = str.encode(bytes_packet(some_data)) + some_data

        self.sock.send(data)

        return self

    def receive_data(self, echo=False, decode=True):
        """
        Receive bytes and convert them into a string if decode is set to True

        :param echo:
        :param decode:
        :return:
        """

        data = b''
        while True:
            try:
                data += self.sock.recv(1)
            except socket.error as error_message:
                if self.echo:
                    print('Server closed connection:', error_message)
                self.sock.close()
                self.sock = self.connect_to_server()
                return ''
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

        data = b''
        data_len = len(str.encode(start_data))

        try:
            if type(recv_length) == tuple:
                chunks, extra = recv_length
                for i in range(chunks):
                    data += self.sock.recv(self.recv_size)
                data += self.sock.recv(extra)
            else:
                data += self.sock.recv(recv_length)

            if download_extra_byte:
                data += self.sock.recv(1)

            data_len += len(data)
        except socket.error as error_message:
            if self.echo:
                print('Server closed connection:', error_message)
            self.sock.close()
            self.sock = self.connect_to_server()
            return ''

        output = str.encode(start_data) + data if type(data) == bytes else str.encode(data)
        if echo:
            print('< Response: {} >'.format(output))
        if decode:
            output = output.decode('utf-8')
        return output

    def terminate(self):
        self.send_data('')

