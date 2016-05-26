# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## PingSocket implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import socket
from errno import *
import struct
import os
import itertools
import functools
import errno
import logging
## Third-party modules
from tornado.ioloop import IOLoop
import tornado.gen
import tornado.concurrent
from tornado.util import errno_from_exception

logger = logging.getLogger(__name__)

ICMPv4_PROTO = socket.IPPROTO_ICMP
ICMPv4_ECHOREPLY = 0
ICMPv4_UNREACHABLE = 3
ICMPv4_TTL_EXCEEDED = 11
ICMPv4_ECHO = 8
ICMPv6_PROTO = socket.IPPROTO_ICMPV6
ICMPv6_ECHO = 128
ICMPv6_ECHOREPLY = 129
MAX_RECV = 1500
_ERRNO_WOULDBLOCK = (errno.EWOULDBLOCK, errno.EAGAIN)


class PingSocket(object):
    """
    IPv4/IPv6 ping socket base
    """
    ECHO_TYPE = None
    HEADER_SIZE = None
    # Recommended send buffer size, 4M by default
    SNDBUF = 4 * 1048576
    # Recommended receive buffer size, 4M by default
    RCVBUF = 4 * 1048576

    def __init__(self, io_loop=None, tos=None):
        self.io_loop = io_loop or IOLoop.current()
        self.socket = None
        self._ready = False
        self.tos = tos
        self.create_socket()
        self._ready = True
        self.io_loop.add_handler(
            self.socket.fileno(),
            self.on_read,
            IOLoop.READ
        )
        self.sessions = {}  # (address, request_id, seq) -> future
        self.out_buffer = []  # [(address, msg)]
        self.writing = False

    def is_ready(self):
        """
        Service must call is_ready to determine ping socket is
        created properly
        """
        return self._ready

    def create_socket(self):
        raise NotImplementedError

    def adjust_buffers(self):
        """
        Set send and receive buffers
        """
        def set_buffer_size(sock, direction, start_size):
            s = start_size
            while s:
                try:
                    sock.setsockopt(socket.SOL_SOCKET, direction, s)
                    return sock.getsockopt(socket.SOL_SOCKET, direction)
                except socket.error:
                    s >>= 2

        send_size = set_buffer_size(
            self.socket, socket.SO_SNDBUF, self.SNDBUF
        )
        recv_size = set_buffer_size(
            self.socket, socket.SO_RCVBUF, self.RCVBUF
        )
        logger.info(
            "Adjust ping socket buffers: send=%s, recv=%s",
            send_size, recv_size
        )

    def ping(self, address, timeout, size, request_id, seq):
        """
        Send echo request and returns future
        """
        # @todo: Check timeout
        logger.debug("[%s] Ping (req=%s, seq=%s, timeout=%sms)",
                     address, request_id, seq, timeout)
        msg = self.build_echo_request(size, request_id, seq)
        sid = (address, request_id, seq)
        f = tornado.concurrent.TracebackFuture()
        f.sid = sid
        self.sessions[sid] = f
        self.send(address, msg)
        self.io_loop.call_later(
            timeout / 1000.0,
            functools.partial(self.on_timeout, f)
        )
        return f

    def parse_reply(self, msg, ip):
        """
        Returns status, address, request_id, sequence
        """
        raise NotImplementedError

    def on_read(self, fd, events):
        try:
            msg, addr = self.socket.recvfrom(MAX_RECV)
        except socket.error, why:
            if why[0] in (EINTR, EAGAIN):
                return  # Exit silently
            raise socket.error, why
        status, address, req_id, seq, rtt = self.parse_reply(msg, addr[0])
        if status is None:
            return
        logger.debug("[%s] Reply (req=%s, seq=%s, status=%s, rtt=%s)",
                     address, req_id, seq, status, rtt)
        sid = (address, req_id, seq)
        if sid in self.sessions:
            f = self.sessions.pop(sid)
            # Resolve future
            f.set_result(rtt)
        else:
            logger.debug(
                "[%s] Ignoring stale session (req=%s, seq=%s)",
                address, req_id, seq
            )

    def on_timeout(self, future):
        """
        Check future is not timed out
        """
        if future.running():
            if future.sid in self.sessions:
                logger.debug("[%s] Timed out", future.sid[0])
                del self.sessions[future.sid]
            future.set_result(None)

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

    def build_echo_request(self, size, request_id, seq):
        checksum = 0
        # Fake header with zero checksum
        header = struct.pack(
            "!BBHHH",
            self.ECHO_TYPE, 0,
            checksum, request_id, seq)
        # Pad to size
        ts = self.io_loop.time()
        payload = (struct.pack("!d", ts) + "A" * (size - self.HEADER_SIZE - 8))[:size - self.HEADER_SIZE]
        # Get checksum
        checksum = self.get_checksum(header + payload)
        # Rebuild header with proper checksum
        header = struct.pack(
            "!BBHHH",
            self.ECHO_TYPE, 0,
            checksum, request_id, seq)
        return header + payload

    def send(self, address, msg):
        self.out_buffer += [(address, msg)]
        self.on_send()

    def on_send(self, *args, **kwargs):
        new_buffer = []
        for a, m in self.out_buffer:
            try:
                self.socket.sendto(m, (a, 0))
            except socket.error as e:
                c = errno_from_exception(e)
                if c in _ERRNO_WOULDBLOCK:
                    logger.info("[%s] Out of buffer space, waiting", a)
                    new_buffer += [(a, m)]
                else:
                    logger.error("[%s] Failed to send request: %s",
                                 a, e)
        self.out_buffer = new_buffer
        if new_buffer:
            if not self.writing:
                self.io_loop.add_handler(self.socket.fileno(),
                                         self.on_send,
                                         self.io_loop.WRITE)
                self.writing = True
        elif self.writing:
            self.io_loop.remove_handler(self.socket.fileno())
            self.writing = False


class Ping4Socket(PingSocket):
    """
    ICMPv4 Ping Socket
    """
    ECHO_TYPE = ICMPv4_ECHO
    HEADER_SIZE = 28

    def create_socket(self):
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, ICMPv4_PROTO
        )
        if self.tos:
            self.socket.setsockopt(
                socket.IPPROTO_IP, socket.IP_TOS, self.tos
            )
        self.adjust_buffers()

    def parse_reply(self, msg, addr):
        """
        Returns status, address, request_id, sequence
        """
        ip_header = msg[:20]
        (ver, tos, plen, pid, flags,
         ttl, proto, checksum, src_ip,
         dst_ip) = struct.unpack("!BBHHHBBHII", ip_header)
        if proto != ICMPv4_PROTO:
            return
        icmp_header = msg[20:28]
        (icmp_type, icmp_code, icmp_checksum,
        req_id, seq) = struct.unpack(
            "!BBHHH", icmp_header)
        if icmp_type == ICMPv4_ECHOREPLY:
            rtt = None
            if len(msg) > 36:
                t0 = struct.unpack("!d", msg[28:36])[0]
                rtt = self.io_loop.time() - t0
            return True, addr, req_id, seq, rtt
        elif icmp_type in (ICMPv4_UNREACHABLE, ICMPv4_TTL_EXCEEDED):
            if plen >= 48:
                (_, _, _, _, _, _, o_proto, _, o_src_ip, o_dst_ip) = struct.unpack("!BBHHHBBHII", msg[28:48])
                if o_proto == ICMPv4_PROTO:
                    (o_icmp_type, _, _, o_req_id, _) = struct.unpack("!BBHHH", msg[48:56])
                    if o_icmp_type == ICMPv4_ECHO:
                        return False, addr, req_id, seq, None
        return None, None, None, None, None


class Ping6Socket(PingSocket):
    """
    ICMPv6 Ping Socket
    """
    ECHO_TYPE = ICMPv6_ECHO
    HEADER_SIZE = 48

    def create_socket(self):
        self.socket = socket.socket(
            socket.AF_INET6, socket.SOCK_RAW, ICMPv6_PROTO
        )
        if self.tos:
            self.socket.setsockopt(
                socket.IPPROTO_IP, socket.IP_TOS, self.tos
            )
        self.adjust_buffers()

    def parse_reply(self, msg, addr):
        """
        Returns status, address, request_id, sequence, rtt
        """
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
        rtt = None
        if len(payload) >= 8:
            t0 = struct.unpack("!d", payload[:8])[0]
            rtt = self.io_loop.time() - t0
        if icmp_type == ICMPv6_ECHOREPLY:
            return True, addr, req_id, seq, rtt
        else:
            return None, None, None, None, None


class Ping(object):
    CHECK_FIRST = 0
    CHECK_ALL = 1

    iter_request = itertools.count(os.getpid())

    def __init__(self, io_loop=None, tos=None):
        self.io_loop = io_loop or IOLoop.current()
        self.ping4 = None
        self.ping6 = None
        self.tos = tos

    def get_socket(self, address):
        """
        Return PingSocket instance
        """
        try:
            if ":" in address:
                if not self.ping6:
                    self.ping6 = Ping6Socket(self.io_loop, tos=self.tos)
                return self.ping6
            else:
                if not self.ping4:
                    self.ping4 = Ping4Socket(self.io_loop, tos=self.tos)
                return self.ping4
        except socket.error as e:
            logger.error("Failed to create ping socket: %s", e)
            return None

    @tornado.gen.coroutine
    def ping_check(self, address, size=64, count=1, timeout=1000,
                   policy=CHECK_FIRST):
        """
        Perform ping check and return status
        :param address: IPv4/IPv6 address of host
        :param size: Packet size, in octets
        :param count: Maximal number of packets to send
        :param timeout: Ping timeout, in milliseconds
        :param policy: Check policy. CHECK_FIRST - return True on
            first success. CHECK_ALL - return True when all checks succeded
        :returns: Ping status as boolean
        """
        socket = self.get_socket(address)
        if not socket:
            raise tornado.gen.Return(None)
        req_id = self.iter_request.next() & 0xFFFF
        result = False
        for seq in range(count):
            r = yield socket.ping(address, timeout, size, req_id, seq)
            if r and policy == self.CHECK_FIRST:
                result = True
                break
            elif not r and policy == self.CHECK_ALL:
                result = False
                break
        logger.debug("[%s] Result: %s", address, result)
        raise tornado.gen.Return(result)

    @tornado.gen.coroutine
    def ping_check_rtt(self, address, size=64, count=1, timeout=1000,
                       policy=CHECK_FIRST):
        """
        Perform ping check and return round-trip time
        :param address: IPv4/IPv6 address of host
        :param size: Packet size, in octets
        :param count: Maximal number of packets to send
        :param timeout: Ping timeout, in milliseconds
        :param policy: Check policy. CHECK_FIRST - return True on
            first success. CHECK_ALL - return True when all checks succeded
        :returns: rtt in seconds as float or None for failure
        """
        socket = self.get_socket(address)
        if not socket:
            raise tornado.gen.Return(None)
        req_id = self.iter_request.next() & 0xFFFF
        result = False
        rtts = []
        for seq in range(count):
            rtt = yield socket.ping(address, timeout, size, req_id, seq)
            if rtt is not None:
                rtts += [rtt]
            if rtt and policy == self.CHECK_FIRST:
                result = True
                break
            elif not rtt and policy == self.CHECK_ALL:
                result = False
                break
        if result:
            rtt = sum(rtts) / len(rtts)
            logger.debug("[%s] Result: success, rtt=%s", address, rtt)
            raise tornado.gen.Return(rtt)
        else:
            logger.debug("[%s] Result: failed", address)
            raise tornado.gen.Return(None)
