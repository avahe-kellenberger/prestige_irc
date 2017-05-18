import socket
import threading

class Connection(object):
    
    """Creates a connection

    Connects to a server at a specific port, and keeps the connection alive.
    
    """
    
    def __init__(self, server, port):
        self.server = server
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10)
        self.__listeners = {}
        self.__is_alive = False
        self.__listen_thread = threading.Thread(self.__listen())
    
    def connect(self):
        """Connect to to server.
        
        Throws a socket error if a connection could not be made. 
        Returns if the connection state changed.
        
        """
        
        if (self.__is_alive):
            try:
                self.socket.connect((self.server, self.port))
                self.__is_alive = True;
                self.listen_thread.start()
            except socket.error as exc:
                print("Caught exception socket.error : " + exc)
                self.__is_alive = False
            return self.__is_alive
    
        return False
        
    def disconnect(self):
        """Disconnects; returns True if the connnection state changed."""
        if (self.__is_alive):
            self.socket.close()
            self.__is_alive = False
            return True
        return False
        
    @property
    def is_alive(self):
        """Return if the connection is currently connected."""
        return self.__is_alive
    
    def send_data(self, data):
        """Sends bytes across the connection."""
        self.socket.send_data(data);
    
    def send(self, string):
        """Helper function, sends a string across the connection as bytes."""
        self.send_data(bytes(string, "utf-8"));
    
    def add_listener(self, listener):
        """Adds a bytes listener to the connection."""
        self.listeners.append(listener)
        
    def __listen(self):
        """Listen to the connection in a loop."""
        while self.is_connected:
            data = self.socket.recv(4096)
            for listener in self.listeners:
                listener(data)