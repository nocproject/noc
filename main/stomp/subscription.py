class Subscription(object):
    def __init__(self, daemon, socket, id, destination, ack):
        self.daemon = daemon
        self.id = id
        self.socket = socket
        self.destination = destination
        self.ack = ack

    def send(self, headers, message):
        h = headers.copy()  # @todo: python 2.5?
        h["subscription"] = self.id
        self.socket.send_message("MESSAGE", h, message)
