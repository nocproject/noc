# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SSH transport
## Based upon twisted.conch.ssh code
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from hashlib import sha1, sha256, md5
import zlib
## NOC modules
from noc.lib.nbsocket import ConnectedTCPSocket
from noc.sa.script.cli import CLI
from noc.sa.script.ssh.util import *
from noc.sa.script.ssh.transform import SSHTransform
from noc.sa.script.ssh.keys import Key

##
SSH_STATES = {
    "SSH_START": {
        "SSH_VERSION": "SSH_VERSION",
        },
    "SSH_VERSION": {
        "FAILURE": "FAILURE",
        "SSH_KEY_EXCHANGE": "SSH_KEY_EXCHANGE"
    },
    "SSH_KEY_EXCHANGE": {
        "FAILURE": "FAILURE",
        "SSH_AUTH": "SSH_AUTH",
    },
    "SSH_AUTH": {
        "SSH_AUTH_PASSWORD": "SSH_AUTH_PASSWORD",
        "FAILURE": "FAILURE"
    },
    "SSH_AUTH_PASSWORD": {
        "SSH_CHANNEL": "SSH_CHANNEL",
        "FAILURE": "FAILURE"
    },
    "SSH_CHANNEL": {
        "SSH_PTY": "SSH_PTY",
        "FAILURE": "FAILURE",
        },
    "SSH_PTY": {
        "SSH_SHELL": "SSH_SHELL",
        "FAILURE": "FAILURE"
    },
    "SSH_SHELL": {
        "START": "START",
        "FAILURE": "FAILURE"
    }
}
SSH_STATES.update(CLI.STATES)

##
## SSH messages
##
MSG_DISCONNECT = 1
MSG_IGNORE = 2
MSG_UNIMPLEMENTED = 3
MSG_DEBUG = 4
MSG_SERVICE_REQUEST = 5
MSG_SERVICE_ACCEPT = 6
MSG_KEXINIT = 20
MSG_NEWKEYS = 21
MSG_KEXDH_INIT = 30
MSG_KEXDH_REPLY = 31
MSG_KEX_DH_GEX_REQUEST_OLD = 30
MSG_KEX_DH_GEX_REQUEST = 34
MSG_KEX_DH_GEX_GROUP = 31
MSG_KEX_DH_GEX_INIT = 32
MSG_KEX_DH_GEX_REPLY = 33
MSG_USERAUTH_REQUEST = 50
MSG_USERAUTH_FAILURE = 51
MSG_USERAUTH_SUCCESS = 52
MSG_USERAUTH_BANNER = 53
MSG_USERAUTH_PK_OK = 60
MSG_USERAUTH_INFO_RESPONSE = 61
MSG_CHANNEL_OPEN = 90
MSG_CHANNEL_OPEN_CONFIRMATION = 91
MSG_CHANNEL_OPEN_FAILURE = 92
MSG_CHANNEL_WINDOW_ADJUST = 93
MSG_CHANNEL_DATA = 94
MSG_CHANNEL_EXTENDED_DATA = 95
MSG_CHANNEL_EOF = 96
MSG_CHANNEL_CLOSE = 97
MSG_CHANNEL_REQUEST = 98
MSG_CHANNEL_SUCCESS = 99
MSG_CHANNEL_FAILURE = 100

DISCONNECT_HOST_NOT_ALLOWED_TO_CONNECT = 1
DISCONNECT_PROTOCOL_ERROR = 2
DISCONNECT_KEY_EXCHANGE_FAILED = 3
DISCONNECT_RESERVED = 4
DISCONNECT_MAC_ERROR = 5
DISCONNECT_COMPRESSION_ERROR = 6
DISCONNECT_SERVICE_NOT_AVAILABLE = 7
DISCONNECT_PROTOCOL_VERSION_NOT_SUPPORTED = 8
DISCONNECT_HOST_KEY_NOT_VERIFIABLE = 9
DISCONNECT_CONNECTION_LOST = 10
DISCONNECT_BY_APPLICATION = 11
DISCONNECT_TOO_MANY_CONNECTIONS = 12
DISCONNECT_AUTH_CANCELLED_BY_USER = 13
DISCONNECT_NO_MORE_AUTH_METHODS_AVAILABLE = 14
DISCONNECT_ILLEGAL_USER_NAME = 15

L = locals()
l = L.keys()
msg_names = dict([(L[n], n) for n in l if n.startswith("MSG_")])
disconnects = dict([(L[n], n[11:]) for n in l if n.startswith("DISCONNECT_")])
del l
del L
quiet_message_types = set([MSG_CHANNEL_DATA])


class CLISSHSocket(CLI, ConnectedTCPSocket):
    """
    SSH protocol socket
    """
    TTL = 30
    DEFAULT_STATE = "SSH_START"

    STATES = SSH_STATES
    ## SSH Client settings
    PROTOCOL_VERSION = "2.0"
    CLIENT_VERSION = "SSH_v2.0@nocproject.org"
    SUPPORTED_VERSIONS = ("1.99", "2.0")
    SSH_VERSION_STRING = "SSH-%s-%s" % (PROTOCOL_VERSION, CLIENT_VERSION)
    SSH_KEY_EXCHANGES = [
        "diffie-hellman-group14-sha1",
        "diffie-hellman-group1-sha1",
        "diffie-hellman-group-exchange-sha256",
        "diffie-hellman-group-exchange-sha1"
    ]
    SSH_CYPHERS = [
        "aes256-ctr", "aes256-cbc",
        "aes192-ctr", "aes192-cbc",
        "aes128-ctr", "aes128-cbc",
        "cast128-ctr", "cast128-cbc",
        "blowfish-ctr", "blowfish-cbc",
        "3des-ctr", "3des-cbc"
    ]
    SSH_PUBLIC_KEYS = [
        # "ecdsa-sha2-nistp256",
        # "ecdsa-sha2-nistp384",
        # "ecdsa-sha2-nistp521",
        "ssh-rsa",
        "ssh-dss"
    ]
    SSH_COMPRESSIONS = ["zlib@openssh.com", "none", "zlib"]
    SSH_MACS = ["hmac-sha1", "hmac-md5"]
    SSH_LANGUAGES = []
    # SSH_AUTH_METHODS = ["publickey", "password", "keyboard-interactive", "none"]
    SSH_AUTH_METHODS = ["none", "publickey", "password", "keyboard-interactive"]

    rx_ssh_version = re.compile(r"^SSH-(?P<version>\d+\.\d+)-(?P<soft>.+$)")

    def __init__(self, script):
        self.script = script
        self._log_label = "SSH: %s" % self.script.access_profile.address
        CLI.__init__(self, self.script.profile, self.script.access_profile)
        port = self.script.access_profile.port or 22
        self.transform = None  # Current SSH Transform
        self.next_transform = None
        self.in_seq = 0
        self.out_seq = 0
        self.out_compression = None
        self.in_compression = None
        # zlib@openssh.com, must be delayed until MSG_USERAUTH_SUCCESS
        self.delayed_out_compression = None
        self.delayed_in_compression = None
        self.kex_hash = sha1  # KEX has function
        self.buffer = ""
        self.d_buffer = ""
        self.session_id = None
        self.local_channel_id = 0
        self.local_window_size = 131072
        self.local_window_left = self.local_window_size
        self.local_max_packet = 32768
        self.remote_window_left = None
        self.remote_max_packet = None
        self.requested_service_name = None
        self.is_ssh_ready = False
        self.local_to_remote_channel = {}
        self.remote_to_local_channel = {}
        self.current_remote_channel = None
        self.last_auth = None
        self.authenticated_with = set()
        self.out_data_buffer = ""
        ConnectedTCPSocket.__init__(self, self.script.activator.factory,
                                    self.script.access_profile.address, port)
        if self.script.CLI_TIMEOUT:
            ConnectedTCPSocket.set_timeout(self, self.script.CLI_TIMEOUT)

    def dump_data(self, data):
        return " ".join(["%02X" % ord(c) for c in data])

    def on_read(self, data):
        """
        Received data dispatcher
        :param data:
        :return:
        """
        self.buffer += data
        if self.get_state() == "SSH_START":
            if self.buffer.startswith("SSH-") and "\n" in self.buffer:
                # Pass further only if full string collected
                self.event("SSH_VERSION")
        else:
            for p in  self.get_packet():
                msg_type = ord(p[0])
                try:
                    h = self.SSH_MESSAGES[msg_type]
                except KeyError:
                    self.error("Uniplemented packet type: %d (%s %s)" % (
                        msg_type, self.dump_data(p),
                        repr(p)))
                    self.send_uniplemented()
                    continue
                if msg_type not in quiet_message_types:
                    self.debug("Receiving message type %s (%d)" % (
                        msg_names[msg_type], msg_type))
                h(self, p[1:])

    def raw_write(self, msg):
        """
        Send raw data to socket
        :param msg:
        :return:
        """
        return ConnectedTCPSocket.write(self, msg)

    def write(self, msg):
        """
        Transfer data to server via encrypted channel
        :param msg:
        :return:
        """
        if not self.is_ssh_ready:
            return
        self.out_data_buffer += msg
        if not self.remote_window_left:
            # No window left, buffer data
            return
        l = len(self.out_data_buffer)
        if l > self.remote_window_left:
            data = self.out_data_buffer[:self.remote_window_left]
            self.out_data_buffer = self.out_data_buffer[
                                   self.remote_window_left:]
        else:
            data = self.out_data_buffer
            self.out_data_buffer = ""
        self.remote_window_left -= len(data)
        self.send_packet(MSG_CHANNEL_DATA, (
            struct.pack(">L", self.current_remote_channel) +
            NS(str(data))
            ))

    def flush_data_buffer(self):
        """
        Flush buffered data
        :return:
        """
        self.write("")

    def is_stale(self):
        if self.get_state() == "PROMPT":
            self.async_check_fsm()
        return ConnectedTCPSocket.is_stale(self)

    def log_label(self):
        return self._log_label

    def debug(self, msg):
        logging.debug("[%s] %s" % (self.log_label(), msg))

    def error(self, msg):
        logging.error("[%s] %s" % (self.log_label(), msg))

    def on_close(self):
        state = self.get_state()
        if state == "SSH_START":
            self.motd = "Connection timeout"
            self.set_state("FAILURE")
        elif self.stale:
            self.queue.put(None)  # Signal stale socket timeout

    def on_conn_refused(self):
        self.debug("Connection refused")
        self.motd = "Connection refused"
        self.set_state("FAILURE")

    def generate_private_x(self, bits):
        def get_random(bits):
            if bits % 8:
                raise ValueError("Bits (%d) must be a multiple of 8" % bits)
            bytes = secure_random(bits / 8)
            return bytes_to_long(bytes)

        MB = (2 ** bits) - 2
        while True:
            x = get_random(bits)
            if 2 <= x <= MB:
                return x

    def send_packet(self, message_type, payload):
        """
        Send single SSH protocol message
        :param message_type:
        :param payload:
        :return:
        """
        self.debug("Sending message type %s (%d)" % (
        msg_names[message_type], message_type))
        payload = chr(message_type) + payload
        if self.out_compression:
            payload = self.out_compression.compress(
                payload) + self.out_compression.flush(2)
        bs = self.transform.enc_block_size
        total_size = 5 + len(payload)
        pad_len = bs - (total_size % bs)
        if pad_len < 4:
            pad_len = pad_len + bs
        packet = struct.pack("!LB", total_size + pad_len - 4,
                             pad_len) + payload + secure_random(pad_len)
        enc_packet = self.transform.encrypt(packet) + self.transform.make_MAC(
            self.out_seq, packet)
        self.raw_write(enc_packet)
        self.out_seq += 1

    def send_disconnect(self, reason, desc):
        """
        Send MSG_DISCONNECT and register failure
        :param reason:
        :param desc:
        :return:
        """
        if reason in disconnects:
            r = "%s:%d" % (disconnects[reason], reason)
        else:
            r = str(reason)
        self.send_packet(MSG_DISCONNECT,
                         struct.pack(">L", reason) + NS(desc) + NS("")
        )
        self.ssh_failure("Disconnecting: %s (%s)" % (desc, r))

    def send_uniplemented(self):
        """
        Send MSG_UNIMPLEMENTED
        :return:
        """
        self.send_packet(MSG_UNIMPLEMENTED, struct.pack("!L", self.in_seq))

    def get_packet(self):
        bs = self.transform.dec_block_size
        ms = self.transform.verify_digest_size
        while self.buffer:
            if len(self.buffer) < bs:
                raise StopIteration  # Less than one block in buffer
            if self.d_buffer:
                head = self.d_buffer
                self.d_buffer = ""
            else:
                head = self.transform.decrypt(self.buffer[:bs])
            packet_len, pad_len = struct.unpack("!LB", head[:5])
            if packet_len > 1048576:
                self.send_disconnect(DISCONNECT_PROTOCOL_ERROR,
                                     "Bad packet length %d" % packet_len)
                raise StopIteration
            plen = packet_len + 4
            if len(self.buffer) < plen + ms:
                # Incomplete packet in buffer
                self.d_buffer = head
                raise StopIteration
            if plen % bs:
                self.send_disconnect(DISCONNECT_PROTOCOL_ERROR,
                                     "Bad packet mod (%i%%%i == %i)" % (
                                     plen, bs, plen % bs))
                raise StopIteration
            enc_data = self.buffer[:plen]
            self.buffer = self.buffer[plen:]
            packet = head + self.transform.decrypt(enc_data[bs:])
            if len(packet) != plen:
                self.send_disconnect(DISCONNECT_PROTOCOL_ERROR,
                                     "Bad decryption")
                raise StopIteration
            if ms:
                mac_data = self.buffer[:ms]
                self.buffer = self.buffer[ms:]
                if not self.transform.verify(self.in_seq, packet, mac_data):
                    self.send_disconnect(DISCONNECT_MAC_ERROR, "Bad MAC")
                    raise StopIteration
            payload = packet[5:-pad_len]
            if self.in_compression:
                try:
                    payload = self.in_compression.decompress(payload)
                except:
                    self.send_disconnect(DISCONNECT_COMPRESSION_ERROR,
                                         "Compression error")
                    raise StopIteration
            self.in_seq += 1
            yield payload

    def ssh_failure(self, msg):
        """
        Protocol failure. Save error message and transit to FAILURE stage
        :param msg:
        :return:
        """
        self.error(msg)
        self.motd = msg
        self.event("FAILURE")

    def request_service(self, name):
        self.requested_service_name = name
        self.debug("Requesting service %s" % name)
        self.send_packet(MSG_SERVICE_REQUEST, NS(name))

    def open_channel(self, name, extra=""):
        self.send_packet(MSG_CHANNEL_OPEN, (
            NS("session") +
            struct.pack(">3L", self.local_channel_id, self.local_window_size,
                        self.local_max_packet) +
            extra
            ))
        self.local_channel_id += 1

    def get_next_auth_method(self, preferred_methods=None):
        """
        Returns preferred authentication method, or None
        :param preferred_methods:
        :return:
        """
        for m in self.SSH_AUTH_METHODS:
            if (m not in self.authenticated_with
                and (preferred_methods is None or m in preferred_methods)):
                return m
        return None

    def authenticate(self, preferred_methods=None):
        """
        Try to authenticate with next available mothod
        :param preferred_methods:
        :return:
        """
        m = self.get_next_auth_method(preferred_methods)
        if m:
            # Request authentication method
            self.debug("Authenticating with '%s' method" % m)
            getattr(self, "request_auth_%s" % m.replace("-", "_"))()
        else:
            self.send_disconnect(DISCONNECT_NO_MORE_AUTH_METHODS_AVAILABLE,
                                 "No more authentication methods available")

    def send_auth(self, type, extra):
        self.last_auth = type
        self.send_packet(MSG_USERAUTH_REQUEST, (
            NS(self.access_profile.user) +
            NS("ssh-connection") +
            NS(type) +
            extra))

    def request_auth_password(self):
        self.send_auth("password", (
            "\x00" +
            NS(self.access_profile.password)))

    def request_auth_publickey(self, sign=True):
        """
        Request publickey authentication.
        Payload:
            byte   has signature
            string algorithm name
            string key blob
            [string signature] - if has signature set

        :param sign:
        :return:
        """
        pub_k = self.factory.controller.ssh_public_key
        pub_k_blob = pub_k.blob()
        if sign:
            priv_k = self.factory.controller.ssh_private_key
            signature = priv_k.sign(
                NS(self.session_id) +
                chr(MSG_USERAUTH_REQUEST) +
                NS(self.access_profile.user) +
                NS("ssh-connection") +
                NS("publickey") +
                "\xff" +
                NS(pub_k.ssh_type()) +
                NS(pub_k_blob)
            )
            signature = NS(signature)
        else:
            signature = ""

        self.send_auth("publickey", (
            ("\xff" if sign else "\x00") +
            NS(pub_k.ssh_type()) +
            NS(pub_k_blob) +
            signature
            ))

    def request_auth_none(self):
        self.send_auth("none", "")

    def request_auth_keyboard_interactive(self):
        self.send_auth("keyboard-interactive", NS("") + NS(""))

    def key_setup(self, shared_secret, exchange_hash):
        def get_key(c, shared_secret, exchange_hash):
            k1 = self.kex_hash(shared_secret + exchange_hash + c + self.session_id)
            k1 = k1.digest()
            k2 = sha1(shared_secret + exchange_hash + k1).digest()
            return k1 + k2

        if not self.session_id:
            self.session_id = exchange_hash
        initIVCS = get_key("A", shared_secret, exchange_hash)
        initIVSC = get_key("B", shared_secret, exchange_hash)
        encKeyCS = get_key("C", shared_secret, exchange_hash)
        encKeySC = get_key("D", shared_secret, exchange_hash)
        integKeyCS = get_key("E", shared_secret, exchange_hash)
        integKeySC = get_key("F", shared_secret, exchange_hash)
        self.next_transform.set_keys(initIVCS, encKeyCS, initIVSC, encKeySC,
                                     integKeyCS, integKeySC)
        self.send_packet(MSG_NEWKEYS, "")

    ##
    ## State handlers
    ##
    def on_SSH_VERSION_enter(self):
        def NS_lists(lists):
            return "".join([NS(",".join(l)) for l in lists])

        # Check protocol version
        self.other_version_string, self.buffer = self.buffer.split("\n", 1)
        self.other_version_string = self.other_version_string.strip()
        match = self.rx_ssh_version.match(self.other_version_string)
        if not match:
            return self.ssh_failure(
                "Protocol version negoriation failed: %s" % self.other_version_string)
        s_version = match.group("version")
        if s_version not in self.SUPPORTED_VERSIONS:
            return self.ssh_failure(
                "Unsupported SSH protocol version: %s" % s_version)
        remote_soft = match.group("soft")
        self.debug("Remote protocol version %s, remote software version %s" % (s_version, remote_soft))
        # Send our version
        if remote_soft.startswith("FreSSH") or remote_soft.startswith("OpenSSH_3.4"):
            # FreSSH.0.8 requires version negotiation
            # to be in separate packet
            self.socket.send(self.SSH_VERSION_STRING + "\r\n")
        else:
            self.raw_write(self.SSH_VERSION_STRING + "\r\n")
        # Set encryption to none
        self.transform = SSHTransform(self, "none", "none", "none", "none")
        self.transform.set_keys("", "", "", "", "", "")
        ## Send our key exchange proposals
        self.our_kex_init_payload = chr(MSG_KEXINIT)\
                                    + secure_random(16)\
                                    + NS_lists([self.SSH_KEY_EXCHANGES,
                                                self.SSH_PUBLIC_KEYS,
                                                self.SSH_CYPHERS,
                                                self.SSH_CYPHERS,
                                                self.SSH_MACS,
                                                self.SSH_MACS,
                                                self.SSH_COMPRESSIONS,
                                                self.SSH_COMPRESSIONS,
                                                self.SSH_LANGUAGES,
                                                self.SSH_LANGUAGES])\
        + "\x00\x00\x00\x00\x00"

        self.send_packet(MSG_KEXINIT, self.our_kex_init_payload[1:])
        self.event("SSH_KEY_EXCHANGE")

    def on_SSH_AUTH_enter(self):
        self.request_service("ssh-userauth")

    def on_SSH_AUTH_PASSWORD_enter(self):
        self.authenticate()

    def on_SSH_CHANNEL_enter(self):
        self.open_channel("session")

    def on_SSH_PTY_enter(self):
        self.debug("Requesting PTY")
        self.send_packet(MSG_CHANNEL_REQUEST, (
            struct.pack(">L", self.current_remote_channel) +
            NS("pty-req") +
            "\x01" +
            NS("vt100") +
            struct.pack(">4L", 80, 25, 0, 0) +
            NS("")
            ))

    def on_SSH_SHELL_enter(self):
        self.debug("Requesting shell")
        self.send_packet(MSG_CHANNEL_REQUEST, (
            struct.pack(">L", self.current_remote_channel) +
            NS("shell") +
            "\x01"
            ))

    ##
    ## SSH Message handlers
    ##
    def ssh_DISCONNECT(self, packet):
        """
        MSG_DISCONNECT
        Payload:
            long   code
            string description
        :param packet:
        :return:
        """
        reason, = struct.unpack(">L", packet[:4])
        description, rest = get_NS(packet[4:], 1)
        try:
            r = " (%s)" % disconnects[reason]
        except KeyError:
            r = ""
        self.ssh_failure("Disconnect received: %s%s" % (description, r))

    def ssh_IGNORE(self, packet):
        """
        MSG_IGNORE
        Payload completely ignored
        :param packet:
        :return:
        """
        pass

    def ssh_DEBUG(self, packet):
        """
        MSG_DEBUG
        Payload:
            bool   always_display
            string message
            string language
        :param packet:
        :return:
        """
        # always_display = bool(packet[0])
        message, lang, rest = get_NS(packet[1:], 2)
        self.debug("Remote debug message received: %s" % message)

    def ssh_UNIMPLEMENTED(self, packet):
        """
        MSG_UNIMPLEMENTED
        Payload:
            long seq_num
        :param packet:
        :return:
        """
        seq_num, = struct.unpack(">L", packet)
        self.debug("Received unimplemented for packet no %d" % seq_num)

    def ssh_KEXINIT(self, packet):
        """
        MSG_KEXINIT
        Payload:
            bytes[16] cookie
            string keyExchangeAlgorithms
            string keyAlgorithms
            string incomingEncryptions
            string outgoingEncryptions
            string incomingAuthentications
            string outgoingAuthentications
            string incomingCompressions
            string outgoingCompressions
            string incomingLanguages
            string outgoingLanguages
            bool   firstPacketFollows
            unit32 0 (reserved)
        :param packet:
        :return:
        """
        def best_match(f, s):
            for i in f:
                if i in s:
                    return i

        self.other_kex_init_payload = chr(MSG_KEXINIT) + packet
        (kex_algs, key_algs, enc_cs, enc_sc, mac_cs, mac_sc, comp_cs,
         comp_sc, lang_cs, lang_sc, rest) = [s.split(",") for s in
                                             get_NS(packet[16:], 10)]

        self.debug(
            "Receiving server proposals: kex=%s key=%s enc_cs=%s enc_sc=%s mac_cs=%s mac_sc=%s comp_cs=%s comp_sc%s" % (
            kex_algs,
            key_algs, enc_cs, enc_sc, mac_cs, mac_sc, comp_cs, comp_sc))
        self.kex_alg = best_match(self.SSH_KEY_EXCHANGES, kex_algs)
        self.key_alg = best_match(self.SSH_PUBLIC_KEYS, key_algs)

        self.next_transform = SSHTransform(self,
                                           best_match(self.SSH_CYPHERS, enc_cs),
                                           best_match(self.SSH_CYPHERS, enc_sc),
                                           best_match(self.SSH_MACS, mac_cs),
                                           best_match(self.SSH_MACS, mac_sc)
        )
        self.in_compression_type = best_match(self.SSH_COMPRESSIONS, comp_sc)
        self.out_compression_type = best_match(self.SSH_COMPRESSIONS, comp_cs)

        if None in (self.kex_alg, self.key_alg, self.out_compression_type,
                    self.in_compression_type):
            self.send_disconnect(DISCONNECT_KEY_EXCHANGE_FAILED,
                                 "Couldn't match proposals")
            return
        self.debug("Selecting %s %s, in=(%s %s %s) out=(%s %s %s)" % (
            self.kex_alg, self.key_alg,
            self.next_transform.in_cipher_type,
            self.next_transform.in_mac_type,
            self.in_compression_type,
            self.next_transform.out_cipher_type,
            self.next_transform.out_mac_type,
            self.out_compression_type)
        )

        if self.kex_alg.endswith("-sha256"):
            self.kex_hash = sha256
        if self.kex_alg in DH_GROUPS:
            dh_prime, dh_generator = DH_GROUPS[self.kex_alg]
            self.x = self.generate_private_x(512)
            self.e = MPpow(dh_generator, self.x, dh_prime)
            self.send_packet(MSG_KEXDH_INIT, self.e)
        elif self.kex_alg in ("diffie-hellman-group-exchange-sha1", "diffie-hellman-group-exchange-sha256"):
            self.send_packet(MSG_KEX_DH_GEX_REQUEST_OLD, "\x00\x00\x08\x00")
        else:
            raise Exception("Unknown KEX alg")

    def ssh_KEX_DH_GEX_GROUP(self, packet):
        """
        KEX_DH_GEX_GROUP
        For diffie-hellman-group1-sha1 payload is:
            string  serverHostKey
            integer f (server Diffie-Hellman public key)
            string  signature
        For diffie-hellman-group-exchange-sha1 payload is:
            string g (group generator)
            string p (group prime)
        :param packet:
        :return:
        """
        if self.kex_alg in DH_GROUPS:
            # diffie-hellman-groupX-sha1
            # actually MSG_KEXDH_REPLY
            dh_prime, dh_generator = DH_GROUPS[self.kex_alg]
            pub_key, packet = get_NS(packet, 1)
            f, packet = get_MP(packet)
            signature, packet = get_NS(packet, 1)
            self.debug("Server PK fingerprint: %s" % ":".join(
                [ch.encode("hex") for ch in md5(pub_key).digest()]))
            # Generate keys
            server_key = Key.from_string(pub_key)
            shared_secret = MPpow(f, self.x, dh_prime)
            h = sha1((NS(self.SSH_VERSION_STRING) +
                      NS(self.other_version_string) +
                      NS(self.our_kex_init_payload) +
                      NS(self.other_kex_init_payload) +
                      NS(pub_key) +
                      self.e +
                      MP(f) +
                      shared_secret))
            exchange_hash = h.digest()
            if not server_key.verify(signature, exchange_hash):
                self.send_disconnect(DISCONNECT_KEY_EXCHANGE_FAILED,
                                     "Bad signature")
                return
            self.key_setup(shared_secret, exchange_hash)
        else:
            # diffie-hellman-group-exchange-shaX
            self.p, rest = get_MP(packet)
            self.g, rest = get_MP(rest)
            self.x = self.generate_private_x(320)
            self.e = MPpow(self.g, self.x, self.p)
            self.send_packet(MSG_KEX_DH_GEX_INIT, self.e)

    def ssh_NEWKEYS(self, packet):
        """
        MSG_NEWKEYS
        No payload
        :param packet:
        :return:
        """
        if packet != "":
            self.send_disconnect(DISCONNECT_PROTOCOL_ERROR,
                                 "NEWKEYS takes no data")
            return
        if not self.next_transform.enc_block_size:
            return
        self.debug("Using new keys")
        self.transform = self.next_transform
        self.next_transform = None
        if self.out_compression_type == "zlib":
            self.out_compression = zlib.compressobj(6)
        elif self.out_compression_type == "zlib@openssh.com":
            self.delayed_out_compression = zlib.compressobj(6)
        if self.in_compression_type == "zlib":
            self.in_compression = zlib.decompressobj()
        elif self.in_compression_type == "zlib@openssh.com":
            self.delayed_in_compression = zlib.decompressobj()
        if self.get_state() == "SSH_KEY_EXCHANGE":
            self.event("SSH_AUTH")

    def ssh_SERVICE_ACCEPT(self, packet):
        """
        MSG_SERVICE_ACCEPT
        Payload:
            string service name
        :param packet:
        :return:
        """
        name, rest = get_NS(packet, 1)
        if name != self.requested_service_name:
            self.send_disconnect(DISCONNECT_PROTOCOL_ERROR,
                                 "received accept for service we did not request")
        self.debug("Starting service %s" % name)
        if self.get_state() == "SSH_AUTH":
            self.event("SSH_AUTH_PASSWORD")

    def ssh_KEX_DH_GEX_REPLY(self, packet):
        """
        MSG_KEX_DH_GEX_REPLY
        Payload:
            string   server host key
            integer  server DH public key
        :param packet:
        :return:
        """
        pub_key, packet = get_NS(packet)
        f, packet = get_MP(packet)
        signature, packet = get_NS(packet)
        self.debug("Server PK fingerprint: %s" % ":".join(
            [ch.encode("hex") for ch in md5(pub_key).digest()]))
        server_key = Key.from_string(pub_key)
        shared_secret = MPpow(f, self.x, self.p)
        h = self.kex_hash((
            NS(self.SSH_VERSION_STRING) +
            NS(self.other_version_string) +
            NS(self.our_kex_init_payload) +
            NS(self.other_kex_init_payload) +
            NS(pub_key) +
            "\x00\x00\x08\x00" +
            MP(self.p) +
            MP(self.g) +
            self.e +
            MP(f) +
            shared_secret))
        exchange_hash = h.digest()
        if not server_key.verify(signature, exchange_hash):
            self.send_disconnect(DISCONNECT_KEY_EXCHANGE_FAILED,
                                 "bad signature")
            return
        self.key_setup(shared_secret, exchange_hash)

    def ssh_USERAUTH_FAILURE(self, packet):
        """
        MSG_USERAUTH_FAILURE
        Payload:
            string methods
            byte partial success
        :param packet:
        :return:
        """
        methods, partial = get_NS(packet)
        partial = bool(ord(partial))
        if partial:
            self.debug(
                "Authetication method '%s' has partial success. Trying next method (%s)" % (
                self.last_auth, methods))
        else:
            self.debug(
                "Authentication method '%s' has been failed. Trying next method (%s)" % (
                self.last_auth, methods))

        self.debug(
            "Partially authenticated with '%s'. Trying next method" % self.last_auth)
        self.authenticated_with.add(self.last_auth)
        methods_left = [x for x in [x.strip() for x in methods.split(",")] if
                        x not in self.authenticated_with]
        if methods_left:
            # Try to authenticate other method
            self.authenticate(methods_left)
            return
        self.ssh_failure("Authentication failed")

    def ssh_USERAUTH_SUCCESS(self, packet):
        """
        MSG_USERAUTH_SUCCESS
        :param packet:
        :return:
        """
        if self.delayed_out_compression:
            self.debug("Enabling delayed out compression %s" % self.out_compression_type)
            self.out_compression = self.delayed_out_compression
            self.delayed_out_compression = None
        if self.delayed_in_compression:
            self.debug("Enabling delayed in compression %s" % self.in_compression_type)
            self.in_compression = self.delayed_in_compression
            self.delayed_in_compression = None
        self.event("SSH_CHANNEL")

    def ssh_USERAUTH_BANNER(self, packet):
        """
        MSG_USERAUTH_BANNER
        Payload:
            string message
            string language
        :param packet:
        :return:
        """
        message, language, rest = get_NS(packet, 2)
        self.motd = message

    def ssh_USERAUTH_PK_OK(self, packet):
        """
        MSG_USERAUTH_PK_OK
        Has different meanings depending on current authentication method.
        Try to dispatch
        :param packet:
        :return:
        """
        try:
            h = getattr(self, "ssh_USERAUTH_PK_OK_%s" %\
                              self.last_auth.lower().replace("-", "_"))
        except AttributeError:
            self.request_auth_none()
            return
        h(packet)

    def ssh_USERAUTH_PK_OK_publickey(self, packet):
        """
        MSG_USERAUTH_PK_OK
        publickey authentication
        Payload:
             string pk algorithm
             string pk blob
        :param packet:
        :return:
        """
        # Requesting to sign already signed authentication request.
        self.request_auth_none()

    def ssh_USERAUTH_PK_OK_keyboard_interactive(self, packet):
        """
        MSG_USERAUTH_PK_OK
        keyboard-interactive authentication
        Payload:
             string name
             string instruction
             string lang
             string data
        :param packet:
        :return:
        """
        name, instruction, lang, data = get_NS(packet, 3)
        n_prompts = struct.unpack('!L', data[:4])[0]
        data = data[4:]
        prompts = []
        for i in range(n_prompts):
            s, data = get_NS(data, 1)
            prompts += [(s, bool(ord(data[0])))]
            data = data[1:]
        self.debug("keyboard-interactive instruction: %s" % instruction)
        self.debug("keyboard-interactive prompts: %s" % str(prompts))
        if prompts:
            responses = [self.access_profile.password]
        else:
            responses = []
        data = struct.pack("!L", len(responses))
        for r in responses:
            data += NS(r.encode("utf8"))
        self.send_packet(MSG_USERAUTH_INFO_RESPONSE, data)

    def ssh_CHANNEL_OPEN_CONFIRMATION(self, packet):
        """
        MSG_CHANNEL_OPEN_CONFIRMATION
        Payload:
            uint32  local channel number
            uint32  remote channel number
            uint32  remote window size
            uint32  remote maximum packet size
            <channel specific data>
        :param packet:
        :return:
        """
        (local_channel, remote_channel,
         remote_window, remote_max_packet) = struct.unpack(">4L", packet[:16])
        self.local_to_remote_channel[local_channel] = remote_channel
        self.remote_to_local_channel[remote_channel] = local_channel
        self.remote_window_left = remote_window
        self.remote_max_packet = remote_max_packet
        self.current_remote_channel = remote_channel
        self.debug("Opening channel. local=%d remote=%d" % (
        local_channel, remote_channel))
        self.event("SSH_PTY")

    def ssh_CHANNEL_OPEN_FAILURE(self, packet):
        """
        MSG_CHANNEL_OPEN_FAILURE
        :param packet:
        :return:
        """
        self.ssh_failure("Cannot open channel")

    def ssh_CHANNEL_WINDOW_ADJUST(self, packet):
        """
        MSG_CHANNEL_WINDOW_ADJUST
        Payload:
             uint32 local channel number
             uint32 bytes to add
        :param packet:
        :return:
        """
        local_channel, bytes_to_add = struct.unpack(">2L", packet[:8])
        self.remote_window_left += bytes_to_add
        self.flush_data_buffer()

    def ssh_MSG_CHANNEL_EOF(self, packet):
        """
        MSG_CHANNEL_EOF
        Payload:
             uint32 channel_id
        :param packet:
        :return:
        """
        pass  # Silently ignore

    def ssh_MSG_CHANNEL_CLOSE(self, packet):
        """
        MSG_CHANNEL_CLOSE
        Payload:
             uint32 channel_id
        :param packet:
        :return:
        """
        self.send_packet(MSG_CHANNEL_CLOSE,
                         struct.pack(">L", self.current_remote_channel))

    def ssh_CHANNEL_REQUEST(self, packet):
        """
        MSG_CHANNEL_REQUEST
        Payload:
             uint32 channel_id
             string request type
             bool   want reply
        :param packet:
        :return:
        """
        # @todo: Check local channel id
        channel_id, = struct.unpack(">L", packet[:4])
        request_type, rest = get_NS(packet[4:])
        want_reply = bool(ord(rest[0]))
        if not want_reply:
            return
            # Process keepalives
        if request_type.startswith("keepalive@"):
            self.send_packet(MSG_CHANNEL_FAILURE,
                             struct.pack(">2L", self.current_remote_channel, 0))

    def ssh_CHANNEL_SUCCESS(self, packet):
        """
         MSG_CHANNEL_SUCCESS
        :param packet:
        :return:
        """
        s = self.get_state()
        if s == "SSH_PTY":
            self.event("SSH_SHELL")
        elif s == "SSH_SHELL":
            self.is_ssh_ready = True
            self.event("START")

    def ssh_CHANNEL_DATA(self, packet):
        """
        MSG_CHANNEL_DATA
        Payload:
            int    channel_id
            string data
        :param packet:
        :return:
        """
        # @todo: Check local channel id
        channel_id, = struct.unpack(">L", packet[:4])
        packet, rest = get_NS(packet[4:])
        CLI.on_read(self, packet)
        self.local_window_left -= len(packet)
        if self.local_window_left <= 0:  # @todo: adaptive behavior
            self.local_window_left = self.local_window_size
            self.send_packet(MSG_CHANNEL_WINDOW_ADJUST,
                             struct.pack(">2L", self.current_remote_channel,
                                         self.local_window_left)
            )
            #self.__flush_submitted_data()

    def ssh_CHANNEL_EXTENDED_DATA(self, packet):
        """
        MSG_CHANNEL_EXTENDED_DATA
        Payload:
             int    channel_id
             int    data_type
             string data
        :param packet:
        :return:
        """
        # @todo: Check local channel id
        channel_id, data_type = struct.unpack(">2L", packet[
                                                     :4])
        packet, rest = get_NS(packet[8:])
        self.debug("Read extended: %r" % packet)
        self.feed(packet, cleanup=self.profile.cleaned_input)
        #self.__flush_submitted_data()

    ## Message dispatchers
    SSH_MESSAGES = {
        MSG_DISCONNECT: ssh_DISCONNECT,
        MSG_IGNORE: ssh_IGNORE,
        MSG_UNIMPLEMENTED: ssh_UNIMPLEMENTED,
        MSG_DEBUG: ssh_DEBUG,
        #MSG_SERVICE_REQUEST = 5
        MSG_SERVICE_ACCEPT: ssh_SERVICE_ACCEPT,
        MSG_KEXINIT: ssh_KEXINIT,
        MSG_NEWKEYS: ssh_NEWKEYS,
        #MSG_KEXDH_INIT = 30
        #MSG_KEXDH_REPLY = 31
        #MSG_KEX_DH_GEX_REQUEST_OLD = 30
        #MSG_KEX_DH_GEX_REQUEST = 34
        MSG_KEX_DH_GEX_GROUP: ssh_KEX_DH_GEX_GROUP,
        #MSG_KEX_DH_GEX_INIT = 32
        MSG_KEX_DH_GEX_REPLY: ssh_KEX_DH_GEX_REPLY,
        MSG_USERAUTH_FAILURE: ssh_USERAUTH_FAILURE,
        MSG_USERAUTH_SUCCESS: ssh_USERAUTH_SUCCESS,
        MSG_USERAUTH_BANNER: ssh_USERAUTH_BANNER,
        MSG_USERAUTH_PK_OK: ssh_USERAUTH_PK_OK,
        MSG_CHANNEL_DATA: ssh_CHANNEL_DATA,
        MSG_CHANNEL_EXTENDED_DATA: ssh_CHANNEL_EXTENDED_DATA,
        MSG_CHANNEL_OPEN_CONFIRMATION: ssh_CHANNEL_OPEN_CONFIRMATION,
        MSG_CHANNEL_OPEN_FAILURE: ssh_CHANNEL_OPEN_FAILURE,
        MSG_CHANNEL_WINDOW_ADJUST: ssh_CHANNEL_WINDOW_ADJUST,
        MSG_CHANNEL_EOF: ssh_MSG_CHANNEL_EOF,
        MSG_CHANNEL_CLOSE: ssh_MSG_CHANNEL_CLOSE,
        MSG_CHANNEL_REQUEST: ssh_CHANNEL_REQUEST,
        MSG_CHANNEL_SUCCESS: ssh_CHANNEL_SUCCESS,
    }

# name -> (DH Prime, DH Generator)
DH_GROUPS = {
    "diffie-hellman-group1-sha1": (
        long(
            "179769313486231590770839156793787453197860296048756011706444"
            "423684197180216158519368947833795864925541502180565485980503"
            "646440548199239100050792877003355816639229553136239076508735"
            "759914822574862575007425302077447712589550957937778424442426"
            "617334727629299387668709205606050270810842907692932019128194"
            "467627007L"
        ), 2
    ),
    "diffie-hellman-group14-sha1": (
        long(
            "323170060713110073003389139264238282488179412411402391128420"
            "097514007417066343542226196894173635693471179017379097041917"
            "546058732091950288537589861856221532121754125149017745202702"
            "357960782362488842461894775876411059286460994117232454266225"
            "221932305409190376805242355191256797158701170010580558776510"
            "388618472802579760549035697325615261670813393617995413364765"
            "591603683178967290731783845896806396719009772021941686472258"
            "710314113364293195361934716365332097170774482279885885653692"
            "086452966360772502689555059283627511211740969729980684105543"
            "595848665832916421362182310789909994486524682624169720359118"
            "52507045361090559L"
        ), 2
    )
}
