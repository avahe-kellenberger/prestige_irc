import socket
import threading


class Connection(object):

    """
    A class for basic generic connectivity.
    """

    def __init__(self):
        """
        Readies a connection to a server at a specific port, and keeps the connection alive.
        """
        self.__socket = None
        self.__is_connection_alive = False
        self.__listen_thread = None
        self.__listeners = set()

    def connect(self, ip_address, port, timeout=None):
        """Connect to a server.

        Parameters
        ----------
        ip_address: str
            The IP address of the server.
        port: int
            The port number to bind to.
        timeout: int|None
            The number of seconds to wait to stop attempting to connect if a connection has not yet been made.
            Default value is None.

        Returns
        -------
        bool:
            If the connection was successfully established.

        Throws
        ------
        socket.error:
            If a connection could not be made.
        """
        sock = socket.socket()
        sock.settimeout(timeout)
        return self.connect_socket(sock=sock, ip_address=ip_address, port=port)

    def connect_socket(self, sock, ip_address, port):
        """Connect to a server using the given socket.

        Parameters
        ----------
        sock: socket.py
            The unconnected socket with which to establish the connection.
        ip_address: str
            The IP address of the server.
        port: int
            The port number to bind to.

        Returns
        -------
        bool:
            If the connection was successfully established.

        Throws
        ------
        socket.error:
            If a connection could not be made.
        """
        if not self.__is_connection_alive:
            try:
                self.__socket = sock
                self.__socket.connect((ip_address, port))
                self.__is_connection_alive = True
                self.__listen_thread = threading.Thread(target=self.__listen)
                self.__listen_thread.start()
            except socket.error as err:
                print(f'Caught exception socket.error:\n{str(err)}')
                self.__is_connection_alive = False
            return self.__is_connection_alive

        return False

    def disconnect(self):
        """Disconnects from the server.

        Returns
        -------
        bool:
           If the connection was successfully terminated.
        """
        if self.__is_connection_alive:
            self.__socket.close()
            self.__is_connection_alive = False
            return True
        return False

    @property
    def is_connection_alive(self):
        """Checks if connection is still live.

        Returns
        -------
        bool:
            If the connection is currently connected.
        """
        return self.__is_connection_alive

    def send_data(self, data):
        """Sends bytes across the connection.

        Parameters
        ----------
        data: bytes
            The bytes to send.
        """
        self.__socket.send(data)

    def send(self, message, crlf_ending=True):
        """Helper function; sends a string across the connection as bytes.

        Parameters
        ----------
        message: str
            The message to send across the connection.
        crlf_ending: bool
            If the method should ensure the message ends with CR-LF.
            Default value is True.
        """
        self.send_data(bytes(f'{message}\r\n' if crlf_ending and not message.endswith('\r\n') else message, 'utf-8'))

    def add_listener(self, listener):
        """Adds a listener to the connection.

        Parameters
        ----------
        listener:
            A function which accepts an object which is created from Connection._process_data(bytes),
            which is called each time data is received from the server.
        """
        self.__listeners.add(listener)

    def remove_listener(self, listener):
        """Removes a listener from the connection.

        Parameters
        ----------
        listener:
            A function which accepts an object which is created from Connection._process_data(bytes),
            which is called each time data is received from the server.
        """
        self.__listeners.remove(listener)

    def _process_data(self, data):
        """Processed the bytes received by the server.

        Parameters
        ----------
        data: bytes
            The bytes received from the server.

        Returns
        -------
        object:
            An object used by the listeners.
        """
        return data

    def __dispatch_listeners(self, obj):
        """Dispatches the listeners waiting for the object.

        Parameters
        ----------
        obj: object
            The object to send to the listeners.
        """
        for listener in self.__listeners:
            if listener.accept(connection=self, message=obj):
                listener.receive(connection=self, message=obj)

    def __listen(self, buffer_size=4096):
        """Listens to incoming data from the socket.

        Parameters
        ----------
        buffer_size: int
            The number of bytes for the socket to receive.
            Default value is `4096`.
        """

        while self.__is_connection_alive:
            data = self.__socket.recv(buffer_size)
            if data:
                # Messages are separated by CR-LF. Last element is removed since it will be empty.
                for msg in data.split(b'\r\n')[:1]:
                    if msg:
                        self.__dispatch_listeners(self._process_data(msg))
            else:
                # Connection terminated by server: data was empty.
                self.__is_connection_alive = False


class MessageListener(object):

    """
    Listens for messages, and uses a filter to determine if the message should be accepted by the listener.
    If the message should be accepted, the implementation should then call MessageListener#receive.
    """

    def __init__(self, receive, message_filter=None):
        """
        Creates the listener.

        Parameters
        ----------
        receive: (Connection, object) -> None
            A method which takes a message as a parameter.
            This should only be called after message_filter returns True.
        message_filter: (Connection, object|None) -> bool
            A method which takes a connection and a message as parameters,
            and returns if the message should be accepted or not.
            If the `message_filter` is `None`, all messages will be accepted and passed to `receive`.
            Default value of `message_filter` is `None`.
        """
        self.__receive = receive
        self.__filter = message_filter

    def accept(self, connection, message):
        """
        Calls the `message_filter` parameter passed into the constructor.

        Parameters
        ----------
        connection: Connection
            The connection the message was sent over.
        message: object
            The message received.

        Returns
        -------
        bool: If the message should be accepted.
        """
        return self.__filter is None or self.__filter(connection, message)

    def receive(self, connection, message):
        """
        Calls the `receive` parameter passed into the constructor.

        Parameters
        ----------
        connection: Connection
            The connection the message was sent over.
        message: object
            The message being received.
        """
        self.__receive(connection, message)
