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
        self.__listeners = {}
    
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
        
        if self.__is_connection_alive:
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
        # TODO: socket.send?
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
        """Adds a bytes listener to the connection.

        Parameters
        ----------
        listener:
            A function which accepts a string that is notified of messages coming across the network.
        """
        # TODO: Look into set appending.
        self.__listeners.append(listener)
        
    def __listen(self):
        """Listen to the connection in a loop."""
        while self.__is_connection_alive:
            data = self.__socket.recv(4096)
            for listener in self.__listeners:
                listener(data)
