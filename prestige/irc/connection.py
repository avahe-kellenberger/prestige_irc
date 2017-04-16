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
        self.listeners = []
        self.is_connected = False
        self.listen_thread = threading.Thread(self.__listen())
    
    def connect(self):
        """Connect to to server.
        
        Throws a socket error if a connection could not be made.
        
        """
        
        try:
            self.socket.connect((self.server, self.port))
            self.is_connected = True;
            self.listen_thread.start()
        except socket.error as exc:
            print("Caught exception socket.error : " + exc)
            self.is_connected = False;
        return self.is_connected;
        
    def is_connected(self):
        """Return if the connection is connected."""
        return self.is_connected
    
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