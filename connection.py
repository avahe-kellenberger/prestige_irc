import socket
import threading


class Connection(object):

    """Creates a connection

    Connects to a server at a specific port, and keeps the connection alive.
    
    """
    
    def __init__(self):
        self.__socket = None
        self.__is_connection_alive = False
        self.__listen_thread = None
        self.__listeners = set()
    
    def connect(self, ip_address, port, timeout):
        """Connect to to server.

        Parameters
        ----------
        ip_address: str
            The IP address of the server.
        port: int
            The port number to bind to.
        timeout: int
            The number of seconds to wait to stop attempting to connect if a connection has not yet been made.

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
                self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.__socket.settimeout(timeout)
                self.__socket.connect((ip_address, port))
                self.__is_connection_alive = True
                self.__listen_thread = threading.Thread(self.__listen())
                self.__listen_thread.start()
            except socket.error as exc:
                print("Caught exception socket.error : " + str(exc))
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
        """
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

    def send(self, message):
        """Helper function; sends a string across the connection as bytes.

        Parameters
        ----------
        message: str
            The message to send across the connection.
        """

        self.send_data(bytes(message + "\r\n", "utf-8"))
    
    def add_listener(self, listener):
        """Adds a listener to the connection.

        Parameters
        ----------
        listener:
            A function which accepts an object which is created from IRCConnection._process_data(bytes),
            which is called each time data is received from the server.
        """
        self.__listeners.add(listener)

    def remove_listener(self, listener):
        """Removes a listener from the connection.

        Parameters
        ----------
        listener:
            A function which accepts an object which is created from IRCConnection._process_data(bytes),
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
        """Listen to the connection in a loop.

        Parameters
        ----------
        obj: object
            The object to send to the listeners.
        """

        listeners = set(self.__listeners)
        while listeners:
            listeners.pop()(obj)

    def __listen(self, buffer_size=4096):
        """Listens to incoming data from the socket.

        Parameters
        ----------
        buffer_size: int
            The number of bytes for the socket to receive.
            Default value is 4096.
        """

        while self.__is_connection_alive:
            # Separate messages by CR-LF
            for msg in self.__socket.recv(buffer_size).split(b"\r\n")[:-1]:
                self.__dispatch_listeners(self._process_data(msg))
