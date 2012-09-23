# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PingSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import socket
from errno import *
import struct
import time
## NOC modules
from noc.lib.nbsocket.basesocket import Socket

ICMP_PROTO = socket.getprotobyname("icmp")
ICMP_ECHOREPLY = 0
ICMP_ECHO = 8
MAX_RECV = 1500


# @todo: Timeout handling
class PingSocket(Socket):
    """
    ICMP Echo Request sender, Echo Reply receiver
    """
    def __init__(self, factory):
        # Pending pings
        self.out_buffer = []  # (address, size, count)
        # Running pings
        self.sessions = {}  # Request Id -> PingSession
        super(PingSocket, self).__init__(factory)

    def create_socket(self):
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, ICMP_PROTO)
        super(PingSocket, self).create_socket()
        if self.out_buffer:
            self.set_status(w=True)

    def handle_write(self):
        while self.out_buffer:
            session = self.out_buffer.pop(0)
            self.sessions[session.req_id] = session
            msg = session.build_echo_request()
            try:
                self.socket.sendto(msg, (session.address, 1))  # Port is irrelevant
            except socket.error, why:  # ENETUNREACH
                self.debug("Socket error: %s" % why)
                self.close()
                return
        self.set_status(w=bool(self.out_buffer))
        self.update_status()

    def handle_read(self):
        self.update_status()
        try:
            msg, addr = self.socket.recvfrom(MAX_RECV)
        except socket.error, why:
            if why[0] in (EINTR, EAGAIN):
                return
            raise socket.error, why
        ip_header = msg[:20]
        (ver, tos, plen, pid, flags,
         ttl, proto, checksum, src_ip,
         dst_ip) = struct.unpack("!BBHHHBBHII", ip_header)

        icmp_header = msg[20:28]
        (icmp_type, icmp_code, icmp_checksum,
        req_id, seq) = struct.unpack(
            "!BBHHH", icmp_header)
        if icmp_type == ICMP_ECHOREPLY and req_id in self.sessions:
            self.sessions[req_id].register_reply(
                address=src_ip, seq=seq, ttl=ttl, msg=msg)

    def ping(self, addr, size=64, count=1, timeout=3, callback=None):
        """
        Start ping

        callback is a callable accepting named parameters:
            address, list of result
        :param addr:
        :param size:
        :param count:
        :param callback:
        :return:
        """
        self.out_buffer += [
            PingSession(self, address=addr, size=size, count=count,
                timeout=timeout, callback=callback)
        ]
        if self.socket:
            self.set_status(w=True)

    def close_session(self, session):
        if session.req_id in self.sessions:
            del self.sessions[session.req_id]

    def is_stale(self):
        """
        Timeouts handling
        """
        t = time.time()
        expired = [self.sessions[r]
                   for r in self.sessions
                   if self.sessions[r].expire and
                      self.sessions[r].expire <= t]
        for s in expired:
            s.register_miss()


# @todo: Rewrite as named tuple
class PingSession(object):
    def __init__(self, ping_socket, address, size,
                 count, timeout, callback):
        self.ping_socket = ping_socket
        self.address = address
        self.size = size
        self.count = count
        self.left = count
        self.timeout = timeout
        self.callback = callback
        self.expire = None
        self.req_id = id(self) & 0xFFFF
        self.seq = 0
        self.payload = None
        self.result = []
        self.t = None

    def register_miss(self):
        self.result += [None]
        self.next()

    def register_reply(self, address, seq, ttl, msg):
        if seq != self.seq or msg[28:] != self.payload:
            return
        # @todo: Check checksum
        t = time.time()
        # Append result
        self.result += [t - self.t]
        self.next()

    def next(self):
        """
        Process next action
        """
        self.seq += 1
        self.expire = None
        if self.seq >= self.count:
            self.ping_socket.close_session(self)
            if self.callback:
                self.callback(self.address, self.result)
        else:
            # Next round
            self.ping_socket.out_buffer += [self]
            self.ping_socket.set_status(w=True)

    def build_echo_request(self):
        checksum = 0
        self.req_id = id(self) & 0xFFFF
        # Fake header with zero checksum
        header = struct.pack("!BBHHH",
            ICMP_ECHO, 0, checksum, self.req_id, self.seq)
        self.payload = "A" * (self.size - 28)  # Pad to size
        # Get checksum
        checksum = self.get_checksum(header + self.payload)
        # Rebuild header with proper checksum
        header = struct.pack("!BBHHH",
            ICMP_ECHO, 0, checksum, self.req_id, self.seq)
        # Save time
        self.t = time.time()
        self.expire = self.t + self.timeout
        return header + self.payload

    def get_checksum(self, msg):
        """
        Calculate checksum
        (RFC-1071)
        """
        lm = len(msg)
        l = lm // 2
        # Calculate the sum of network-ordered shorts
        s = sum(struct.unpack("!" + "H" * l, msg[:2 * l]))
        if lm < l:
            # Add remaining octet
            s += ord(msg[-1])
        # Truncate to 32 bits
        s &= 0xFFFFFFFF
        # Fold 32 bits to 16 bits
        s = (s >> 16) + (s & 0xFFFF)  # Add high 16 bits to low 16 bits
        s += (s >> 16)
        return ~s & 0xFFFF
