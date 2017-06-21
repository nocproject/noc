class RPCError(Exception):
    pass


class RPCHTTPError(RPCError):
    pass


class RPCException(RPCError):
    pass


class RPCNoService(RPCError):
    pass


class RPCRemoteError(RPCError):
    def __init__(self, msg, remote_code=None):
        super(RPCRemoteError, self).__init__(msg)
        self.remote_code = remote_code
