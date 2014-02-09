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
import os
## NOC modules
from noc.lib.nbsocket.basesocket import Socket

ICMPv4_PROTO = socket.IPPROTO_ICMP
ICMPv4_ECHOREPLY = 0
ICMPv4_ECHO = 8
ICMPv6_PROTO = socket.IPPROTO_ICMPV6
ICMPv6_ECHO = 128
ICMPv6_ECHOREPLY = 129
MAX_RECV = 1500


class PingSocket(Socket):
    """
    Abstract ICMP Echo Request sender, Echo Reply receiver
    """
    ECHO_TYPE = None
    HEADER_SIZE = None

    def __init__(self, factory):
        # Pending pings
        self.out_buffer = []  # (address, size, count)
        # Running pings
        self.sessions = {}  # Request Id -> PingSession
        self.req_id = os.getpid() & 0xFFFF
        super(PingSocket, self).__init__(factory)

    def _create_socket(self):
        raise NotImplementedError

    def create_socket(self):
        self._create_socket()
        super(PingSocket, self).create_socket()
        if self.out_buffer:
            self.set_status(w=True)

    def get_session_id(self, session):
        return session.address, session.req_id

    def get_session(self, addr, req_id):
        return self.sessions.get((addr, req_id))

    def handle_write(self):
        self.debug("%d packets to send" % len(self.out_buffer))
        n = 0
        while self.out_buffer and n < 50:  # @todo: Configurable
            n += 1
            session = self.out_buffer.pop(0)
            msg = session.build_echo_request()
            self.sessions[self.get_session_id(session)] = session
            try:
                # Port is irrelevant for icmp
                self.socket.sendto(msg, (session.address, 1))
            except socket.error, why:  # ENETUNREACH
                session.register_miss()
                return
        self.set_status(w=bool(self.out_buffer))
        self.update_status()

    def parse_reply(self, msg, addr):
        raise NotImplementedError

    def handle_read(self):
        self.update_status()
        while True:
            try:
                msg, addr = self.socket.recvfrom(MAX_RECV)
            except socket.error, why:
                if why[0] in (EINTR, EAGAIN):
                    break
                raise socket.error, why
            self.parse_reply(msg, addr[0])

    def ping_session(self, session):
        self.out_buffer += [session]
        if self.socket:
            self.set_status(w=True)

    def ping(self, addr, size=64, count=1, timeout=3, callback=None,
             stop_on_success=False):
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
        self.ping_session(
            PingSession(self, address=addr, size=size,
                count=count, timeout=timeout, callback=callback,
                stop_on_success=stop_on_success)
        )

    def get_session_class(self):
        raise NotImplementedError

    def close_session(self, session):
        sid = self.get_session_id(session)
        if sid in self.sessions:
            del self.sessions[sid]

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
            self.debug("Ping timeout: %s" % s.address)
            s.register_miss()
        if self.sessions:
            self.debug("Current sessions: %d" % len(self.sessions))
        return False

    def on_error(self, exc):
        self.error("Failed to create ping socket. Check process permissions")

    def get_req_id(self):
        r = self.req_id
        self.req_id = (self.req_id + 1) & 0xFFFF
        return r


class Ping4Socket(PingSocket):
    """
    ICMPv4 Ping Socket
    """
    ECHO_TYPE = ICMPv4_ECHO
    HEADER_SIZE = 28

    def _create_socket(self):
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, ICMPv4_PROTO)

    def parse_reply(self, msg, addr):
        ip_header = msg[:20]
        (ver, tos, plen, pid, flags,
         ttl, proto, checksum, src_ip,
         dst_ip) = struct.unpack("!BBHHHBBHII", ip_header)

        icmp_header = msg[20:28]
        (icmp_type, icmp_code, icmp_checksum,
        req_id, seq) = struct.unpack(
            "!BBHHH", icmp_header)
        if icmp_type == ICMPv4_ECHOREPLY:
            session = self.get_session(addr, req_id)
            if session:
                session.register_reply(address=src_ip, seq=seq, ttl=ttl,
                    payload=msg[self.HEADER_SIZE:])


class Ping6Socket(PingSocket):
    """
    ICMPv6 Ping Socket
    """
    ECHO_TYPE = ICMPv6_ECHO
    HEADER_SIZE = 48

    def _create_socket(self):
        self.socket = socket.socket(
            socket.AF_INET6, socket.SOCK_RAW, ICMPv6_PROTO)

    def parse_reply(self, msg, addr):
        # (ver_tc_flow, plen, hdr, ttl) = struct.unpack("!IHBB", msg[:8])
        # src_ip = msg[64: 192]
        # @todo: Access IPv6 header
        src_ip = None
        ttl = None
        # icmp_header = msg[40:48]
        icmp_header = msg[:8]
        (icmp_type, icmp_code, icmp_checksum,
         req_id, seq) = struct.unpack("!BBHHH", icmp_header)
        payload = msg[8:]
        if icmp_type == ICMPv6_ECHOREPLY:
            session = self.get_session(addr, req_id)
            if session:
                session.register_reply(address=src_ip, seq=seq, ttl=ttl,
                    payload=payload)


class PingSession(object):
    def __init__(self, ping_socket, address, size,
                 count, timeout, callback, stop_on_success=False):
        self.ping_socket = ping_socket
        self.address = address
        self.size = size
        self.count = count
        self.left = count
        self.timeout = timeout
        self.callback = callback
        self.stop_on_success = stop_on_success
        self.to_stop = False
        self.expire = None
        self.req_id = self.ping_socket.get_req_id()
        self.seq = 0
        self.payload = None
        self.result = []
        self.t = None

    def register_miss(self):
        self.result += [None]
        self.next()

    def register_reply(self, address, seq, ttl, payload):
        if seq != self.seq or payload != self.payload:
            self.ping_socket.debug("Sequence number mismatch. Ignoring")
            return
        # @todo: Check checksum
        t = time.time()
        # Append result
        self.result += [t - self.t]
        if self.stop_on_success:
            self.to_stop = True
        self.next()

    def next(self):
        """
        Process next action
        """
        self.seq += 1
        self.expire = None
        if self.to_stop or self.seq >= self.count:
            self.ping_socket.close_session(self)
            if self.callback:
                self.callback(self.address, self.result)
        else:
            # Next round
            self.ping_socket.ping_session(self)

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

    def build_echo_request(self):
        checksum = 0
        # Fake header with zero checksum
        header = struct.pack("!BBHHH",
            self.ping_socket.ECHO_TYPE, 0,
            checksum, self.req_id, self.seq)
        # Pad to size
        self.payload = "A" * (self.size - self.ping_socket.HEADER_SIZE)
        # Get checksum
        checksum = self.get_checksum(header + self.payload)
        # Rebuild header with proper checksum
        header = struct.pack("!BBHHH",
            self.ping_socket.ECHO_TYPE, 0,
            checksum, self.req_id, self.seq)
        # Save time
        self.t = time.time()
        self.expire = self.t + self.timeout
        return header + self.payload
