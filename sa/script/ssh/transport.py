# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SSH transport
## Based upon twisted.conch.ssh code
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import re
import struct
from hashlib import sha1, md5
##
from Crypto.Cipher import XOR
from Crypto.Util.number import bytes_to_long
## NOC modules
from noc.lib.nbsocket import ConnectedTCPSocket
from noc.sa.script.cli import CLI
from noc.sa.script.ssh.util import *
from noc.sa.script.ssh.transform import SSHTransform
from noc.sa.script.ssh.keys import Key

##
SSH_STATES={
    "SSH_START" : {
        "SSH_VERSION" : "SSH_VERSION",
    },
    "SSH_VERSION" : {
        "FAILURE"      : "FAILURE",
        "SSH_KEY_EXCHANGE" : "SSH_KEY_EXCHANGE"
    },
    "SSH_KEY_EXCHANGE" : {
        "FAILURE"      : "FAILURE",
        "SSH_AUTH"  : "SSH_AUTH",
    },
    "SSH_AUTH" : {
        "SSH_AUTH_PASSWORD" : "SSH_AUTH_PASSWORD",
        "FAILURE" : "FAILURE"
    },
    "SSH_AUTH_PASSWORD" : {
        "SSH_CHANNEL" : "SSH_CHANNEL",
        "FAILURE"     : "FAILURE"
    },
    "SSH_CHANNEL" : {
        "SSH_PTY"   : "SSH_PTY",
        "FAILURE"     : "FAILURE",
    },
    "SSH_PTY" : {
        "SSH_SHELL" : "SSH_SHELL",
        "FAILURE"   : "FAILURE"
    },
    "SSH_SHELL" : {
        "START"   : "START",
        "FAILURE" : "FAILURE"
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
MSG_CHANNEL_REQUEST = 98
MSG_CHANNEL_SUCCESS = 99

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

L=locals()
l=L.keys()
msg_names=dict([(L[n], n) for n in l if n.startswith("MSG_")])
disconnects=dict([(L[n], n[11:]) for n in l if n.startswith("DISCONNECT_")])
del l
del L
##
##
##
class CLISSHSocket(CLI, ConnectedTCPSocket):
    TTL=30
    DEFAULT_STATE="SSH_START"
    
    STATES=SSH_STATES
    ## SSH Client settings
    PROTOCOL_VERSION="2.0"
    CLIENT_VERSION="SSH_v2.0@nocproject.org"
    SUPPORTED_VERSIONS=("1.99", "2.0")
    SSH_VERSION_STRING="SSH-%s-%s"%(PROTOCOL_VERSION, CLIENT_VERSION)
    SSH_KEY_EXCHANGES = ["diffie-hellman-group-exchange-sha1", "diffie-hellman-group1-sha1"]
    SSH_CYPHERS = ["aes256-ctr", "aes256-cbc", "aes192-ctr", "aes192-cbc", "aes128-ctr", "aes128-cbc",
        "cast128-ctr", "cast128-cbc", "blowfish-ctr", "blowfish-cbc", "3des-ctr", "3des-cbc"]
    SSH_PUBLIC_KEYS = ["ssh-rsa", "ssh-dss"]
    SSH_COMPRESSIONS = ["none", "zlib"]
    SSH_MACS = ["hmac-sha1", "hmac-md5"]
    SSH_LANGUAGES=[]
    SSH_AUTH_METHODS=["publickey", "password", "keyboard-interactive", "none"]
    
    rx_ssh_version=re.compile(r"^SSH-(?P<version>\d+\.\d+)-(?P<soft>.+$)")
    def __init__(self, factory, profile, access_profile):
        self._log_label="SSH: %s"%access_profile.address
        CLI.__init__(self, profile, access_profile)
        port=access_profile.port or 22
        self.transform=None # current SSH Transform
        self.next_transform=None
        self.in_seq=0
        self.out_seq=0
        self.out_compression=None
        self.in_compression=None
        self.buffer=""
        self.d_buffer=""
        self.session_id=None
        self.local_channel_id=0
        self.local_window_size=131072
        self.local_window_left=self.local_window_size
        self.local_max_packet=32768
        self.remote_window_left=None
        self.remote_max_packet=None
        self.requested_service_name=None
        self.is_ssh_ready=False
        self.local_to_remote_channel={}
        self.remote_to_local_channel={}
        self.current_remote_channel=None
        self.last_auth=None
        self.authenticated_with=set()
        self.out_data_buffer=""
        ConnectedTCPSocket.__init__(self, factory, access_profile.address, port)
    
    ##
    ## Received data dispatcher
    ##
    def on_read(self, data):
        self.buffer+=data
        if self.get_state()=="SSH_START":
            if self.buffer.startswith("SSH-") and "\n" in self.buffer:
                # Pass further only if full string collected
                self.event("SSH_VERSION")
        else:
            for p in  self.get_packet():
                msg_type=ord(p[0])
                try:
                    h=self.SSH_MESSAGES[msg_type]
                except KeyError:
                    self.error("Uniplemented packet type: %d"%msg_type)
                    self.send_uniplemented()
                    continue
                self.debug("Receiving message type %s (%d)"%(msg_names[msg_type], msg_type))
                h(self, p[1:])
    
    ##
    ## Send raw data to socket
    ##
    def raw_write(self, msg):
        return ConnectedTCPSocket.write(self, msg)
    
    ##
    ## Transfer data to server
    ##
    def write(self, msg):
        if not self.is_ssh_ready:
            return
        self.out_data_buffer += msg
        if self.remote_window_left == 0:
            # No window left, buffer data
            return
        l=len(self.out_data_buffer)
        if l>self.remote_window_left:
            data = self.out_data_buffer[:self.remote_window_left]
            self.out_data_buffer = self.out_data_buffer[self.remote_window_left:]
        else:
            data = self.out_data_buffer
            self.out_data_buffer = ""
        self.remote_window_left-=len(data)
        self.send_packet(MSG_CHANNEL_DATA,(
            struct.pack(">L", self.current_remote_channel)+
            NS(str(data))
        ))
    
    ##
    ## Flush buffered data
    ##
    def flush_data_buffer(self):
        self.write("")
    
    ##
    ##
    ##
    def is_stale(self):
        if self.get_state()=="PROMPT":
            self.async_check_fsm() 
        return ConnectedTCPSocket.is_stale(self)
    
    ##
    ##
    ##
    def log_label(self):
        return self._log_label
    
    ##
    ##
    ##
    def debug(self,msg):
        logging.debug("[%s] %s"%(self.log_label(),msg))
    
    ##
    ##
    ##
    def error(self, msg):
        logging.error("[%s] %s"%(self.log_label(),msg))
    
    ##
    def generate_private_x(self, bits):
        def get_random(bits):
            if bits%8:
                raise ValueError("Bits (%d) must be a multiple of 8"%bits)
            bytes = secure_random(bits / 8)
            return bytes_to_long(bytes)
        
        MB=(2**bits)-2
        while True:
            x = get_random(bits)
            if 2 <= x <= MB:
                return x
    
    ##
    ## Send single message
    ##
    def send_packet(self, message_type, payload):
        self.debug("Sending message type %s (%d)"%(msg_names[message_type],message_type))
        payload=chr(message_type)+payload
        if self.out_compression:
            payload=self.out_compression.compress(payload)+self.out_compression.flush(2)
        bs=self.transform.enc_block_size
        total_size=5+len(payload)
        pad_len=bs-(total_size%bs)
        if pad_len<4:
            pad_len=pad_len+bs
        packet=struct.pack("!LB", total_size+pad_len-4, pad_len)+payload+secure_random(pad_len)
        enc_packet=self.transform.encrypt(packet)+self.transform.make_MAC(self.out_seq, packet)
        self.raw_write(enc_packet)
        self.out_seq+=1
    
    ##
    ## Send MSG_DISCONNECT and register failure
    ##
    def send_disconnect(self, reason, desc):
        if reason in disconnects:
            r="%s:%d"%(disconnects[reason], reason)
        else:
            r=str(reason)
        self.send_packet(MSG_DISCONNECT,
            struct.pack(">L", reason)+NS(desc)+NS("")
        )
        self.ssh_failure("Disconnecting: %s (%s)"%(desc, r))
    
    ##
    ## Send MSG_UNIMPLEMENTED
    ##
    def send_uniplemented(self):
        self.send_packet(MSG_UNIMPLEMENTED, struct.pack("!L", self.in_seq))
    
    ##
    ##
    ##
    def get_packet(self):
        bs=self.transform.dec_block_size
        ms=self.transform.verify_digest_size
        while self.buffer:
            if len(self.buffer)<bs:
                raise StopIteration
            if self.d_buffer:
                head=self.d_buffer
                self.d_buffer=""
            else:
                head=self.transform.decrypt(self.buffer[:bs])
            packet_len, pad_len=struct.unpack("!LB", head[:5])
            if packet_len > 1048576:
                self.send_disconnect(DISCONNECT_PROTOCOL_ERROR,
                    "Bad packet length %d"%packet_len)
                raise StopIteration
            if len(self.buffer) < packet_len+4+ms:
                self.d_buffer=head
                raise StopIteration
            if (packet_len+4)%bs !=0:
                self.send_disconnect(DISCONNECT_PROTOCOL_ERROR,
                    "Bad packet mod (%i%%%i == %i)" % (packet_len + 4, bs, (packetLen + 4) % bs))
                raise StopIteration
            enc_data=self.buffer[:4+packet_len]
            self.buffer=self.buffer[4+packet_len:]
            packet = head + self.transform.decrypt(enc_data[bs:])
            if len(packet)!=4+packet_len:
                self.send_disconnect(DISCONNECT_PROTOCOL_ERROR, "Bad decryption")
                raise StopIteration
            if ms:
                mac_data=self.buffer[:ms]
                self.buffer=self.buffer[ms:]
                if not self.transform.verify(self.in_seq, packet, mac_data):
                    self.send_disconnect(DISCONNECT_MAC_ERROR, "Bad MAC")
                    raise StopIteration
            payload=packet[5:-pad_len]
            if self.in_compression:
                try:
                    payload=self.in_compression.decompress(payload)
                except:
                    self.send_disconnect(DISCONNECT_COMPRESSION_ERROR, "Compression error")
                    raise StopIteration
            self.in_seq+=1
            yield payload
    
    ##
    ## Protocol failure. Save error message and transit to FAILURE stage
    ##
    def ssh_failure(self, msg):
        self.error(msg)
        self.motd=msg
        self.event("FAILURE")
    
    ##
    ##
    def request_service(self, name):
        self.requested_service_name=name
        self.debug("Requesting service %s"%name)
        self.send_packet(MSG_SERVICE_REQUEST, NS(name))
    
    ##
    def open_channel(self, name, extra=""):
        self.send_packet(MSG_CHANNEL_OPEN, (
            NS("session")+
            struct.pack(">3L", self.local_channel_id, self.local_window_size, self.local_max_packet)+
            extra
        ))
        self.local_channel_id+=1
    
    ##
    ## Returns preferred authentication method, or None
    ##
    def get_next_auth_method(self, preferred_methods=None):
        for m in self.SSH_AUTH_METHODS:
            if (m not in self.authenticated_with
                and (preferred_methods is None or m in preferred_methods)):
                return m
        return None
    
    ##
    ## Try to authenticate with next available mothod
    ##
    def authenticate(self, preferred_methods=None):
        m=self.get_next_auth_method(preferred_methods)
        if m:
            self.debug("Authenticating with '%s' method"%m)
            getattr(self,"request_auth_%s"%m.replace("-", "_"))() # Request authentication method
        else:
            self.send_disconnect(DISCONNECT_NO_MORE_AUTH_METHODS_AVAILABLE, "No more authentication methods available")
    
    ##
    ##
    ##
    def send_auth(self, type, extra):
        self.last_auth=type
        self.send_packet(MSG_USERAUTH_REQUEST,(
            NS(self.access_profile.user)+
            NS("ssh-connection")+
            NS(type)+
            extra))
    
    ##
    ##
    ##
    def request_auth_password(self):
        self.send_auth("password",(
            "\x00"+
            NS(self.access_profile.password)))
    
    ##
    ## Request publickey authentication.
    ## Payload:
    ##     byte   has signature
    ##     string algorithm name
    ##     string key blob
    ##     [string signature] - if has signature set
    ##
    ##
    def request_auth_publickey(self, sign=True):
        pub_k=self.factory.controller.ssh_public_key
        pub_k_blob=pub_k.blob()
        if sign:
            priv_k=self.factory.controller.ssh_private_key
            signature=priv_k.sign(
                NS(self.session_id)+
                chr(MSG_USERAUTH_REQUEST)+
                NS(self.access_profile.user)+
                NS("ssh-connection")+
                NS("publickey")+
                "\xff"+
                NS(pub_k.ssh_type())+
                NS(pub_k.blob())
            )
            signature=NS(signature)
        else:
            signature=""
        
        self.send_auth("publickey", (
            ("\xff" if sign else "\x00")+
            NS(pub_k.ssh_type())+
            NS(pub_k.blob())+
            signature
        ))
    
    ##
    ##
    ##
    def request_auth_none(self):
        self.send_auth("none", "")
    
    ##
    ##
    ##
    def request_auth_keyboard_interactive(self):
        self.send_auth("keyboard-interactive", NS("") + NS(""))
    
    ##
    ##
    ##
    def key_setup(self, shared_secret, exchange_hash):
        def get_key(c, shared_secret, exchange_hash):
            k1 = sha1(shared_secret + exchange_hash + c + self.session_id)
            k1 = k1.digest()
            k2 = sha1(shared_secret + exchange_hash + k1).digest()
            return k1 + k2
        
        if not self.session_id:
            self.session_id = exchange_hash
        initIVCS   = get_key("A", shared_secret, exchange_hash)
        initIVSC   = get_key("B", shared_secret, exchange_hash)
        encKeyCS   = get_key("C", shared_secret, exchange_hash)
        encKeySC   = get_key("D", shared_secret, exchange_hash)
        integKeyCS = get_key("E", shared_secret, exchange_hash)
        integKeySC = get_key("F", shared_secret, exchange_hash)
        self.next_transform.set_keys(initIVCS, encKeyCS, initIVSC, encKeySC,
                                     integKeyCS, integKeySC)
        self.send_packet(MSG_NEWKEYS, "")
    
    
    ##
    ## State handlers
    ##
    
    ##
    ##
    ##
    def on_SSH_VERSION_enter(self):
        def NS_lists(lists):
            return "".join([NS(",".join(l)) for l in lists])
        
        # Check protocol version
        self.other_version_string, self.buffer=self.buffer.split("\n", 1)
        self.other_version_string=self.other_version_string.strip()
        match=self.rx_ssh_version.match(self.other_version_string)
        if not match:
            return self.ssh_failure("Protocol version negoriation failed: %s"%self.other_version_string)
        s_version=match.group("version")
        if s_version not in self.SUPPORTED_VERSIONS:
            return self.ssh_failure("Unsupported SSH protocol version: %s"%s_version)
        self.debug("Remote protocol version %s, remote software version %s"%(s_version, match.group("soft")))
        # Send our version
        self.raw_write(self.SSH_VERSION_STRING+"\n")
        # Set encryption to none
        self.transform=SSHTransform(self, "none", "none", "none", "none")
        self.transform.set_keys("", "", "", "", "", "")
        ## Send our key exchange proposals
        self.our_kex_init_payload=chr(MSG_KEXINIT)\
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
    
    ##
    ##
    ##
    def on_SSH_AUTH_enter(self):
        self.request_service("ssh-userauth")
    
    ##
    ##
    ##
    def on_SSH_AUTH_PASSWORD_enter(self):
        self.authenticate()
    
    ##
    ##
    ##
    def on_SSH_CHANNEL_enter(self):
        self.open_channel("session")
    
    ##
    ##
    ##
    def on_SSH_PTY_enter(self):
        self.debug("Requesting PTY")
        self.send_packet(MSG_CHANNEL_REQUEST,(
            struct.pack(">L", self.current_remote_channel)+
            NS("pty-req")+
            "\x01"+
            NS("vt100")+
            struct.pack(">4L", 80, 25, 0, 0)+
            NS("")
        ))
    
    ##
    ##
    ##
    def on_SSH_SHELL_enter(self):
        self.debug("Requesting shell")
        self.send_packet(MSG_CHANNEL_REQUEST, (
            struct.pack(">L", self.current_remote_channel)+
            NS("shell")+
            "\x01"
        ))
    
    ##
    ## SSH Message handlers
    ##
    
    ##
    ## MSG_DISCONNECT
    ## Payload:
    ##     long   code
    ##     string description
    ##
    def ssh_DISCONNECT(self, packet):
        reason,=struct.unpack(">L", packet[:4])
        description, rest=get_NS(packet[4:], 1)
        try:
            r=" (%s)"%disconnects[reason]
        except KeyError:
            r=""
        self.ssh_failure("Disconnect received: %s%s"%(description,r))
    
    ##
    ## MSG_IGNORE
    ## Payload completely ignored
    ##
    def ssh_IGNORE(self, packet):
        pass
    
    ##
    ## MSG_DEBUG
    ## Payload:
    ##     bool   always_display
    ##     string message
    ##     string language
    ##
    def ssh_DEBUG(self, packet):
        always_display = bool(packet[0])
        message, lang, rest = get_NS(packet[1:], 2)
        self.debug("Remote debug message received: %s"%message)
    
    ##
    ## MSG_UNIMPLEMENTED
    ## Payload:
    ##      long seq_num
    ##
    def ssh_UNIMPLEMENTED(self, packet):
        seq_num, = struct.unpack(">L", packet)
        self.debug("Received unimplemented for packet no %d"%seq_num)
    
    ##
    ## MSG_KEXINIT
    ## Payload:
    ##     bytes[16] cookie
    ##     string keyExchangeAlgorithms
    ##     string keyAlgorithms
    ##     string incomingEncryptions
    ##     string outgoingEncryptions
    ##     string incomingAuthentications
    ##     string outgoingAuthentications
    ##     string incomingCompressions
    ##     string outgoingCompressions
    ##     string incomingLanguages
    ##     string outgoingLanguages
    ##     bool   firstPacketFollows
    ##     unit32 0 (reserved)
    ##
    def ssh_KEXINIT(self, packet):
        def best_match(f, s):
            for i in f:
                if i in s:
                    return i
        
        self.other_kex_init_payload=chr(MSG_KEXINIT)+packet
        (kex_algs, key_algs, enc_cs, enc_sc, mac_cs, mac_sc, comp_cs,
            comp_sc, lang_cs, lang_sc, rest) = [s.split(",") for s in get_NS(packet[16:],10)]
        
        self.debug("Receiving server proposals: kex=%s key=%s enc_cs=%s enc_sc=%s mac_cs=%s mac_sc=%s comp_cs=%s comp_sc%s"%(kex_algs,
            key_algs, enc_cs, enc_sc, mac_cs, mac_sc, comp_cs, comp_sc))
        self.kex_alg=best_match(self.SSH_KEY_EXCHANGES, kex_algs)
        self.key_alg=best_match(self.SSH_PUBLIC_KEYS, key_algs)
        
        self.next_transform=SSHTransform(self,
            best_match(self.SSH_CYPHERS, enc_cs),
            best_match(self.SSH_CYPHERS, enc_sc),
            best_match(self.SSH_MACS,    mac_cs),
            best_match(self.SSH_MACS,    mac_sc)
        )
        self.in_compression_type=best_match(self.SSH_COMPRESSIONS, comp_sc)
        self.out_compression_type=best_match(self.SSH_COMPRESSIONS, comp_cs)
        
        if None in (self.kex_alg, self.key_alg, self.out_compression_type, self.in_compression_type):
            self.send_disconnect(DISCONNECT_KEY_EXCHANGE_FAILED, "Couldn't match proposals")
            return
        self.debug("Selecting %s %s, in=(%s %s %s) out=(%s %s %s)"%(self.kex_alg, self.key_alg,
            self.next_transform.in_cipher_type, self.next_transform.in_mac_type, self.in_compression_type,
            self.next_transform.out_cipher_type, self.next_transform.out_mac_type, self.out_compression_type))
        
        if self.kex_alg=="diffie-hellman-group1-sha1":
            self.x=self.generate_private_x(512)
            self.e=MPpow(DH_GENERATOR, self.x, DH_PRIME)
            self.send_packet(MSG_KEXDH_INIT, self.e)
        elif self.kex_alg == "diffie-hellman-group-exchange-sha1":
            self.send_packet(MSG_KEX_DH_GEX_REQUEST_OLD, "\x00\x00\x08\x00")
        else:
            raise Exception("Unknown KEX alg")
        
    ##
    ## KEX_DH_GEX_GROUP
    ## For diffie-hellman-group1-sha1 payload is:
    ##     string  serverHostKey
    ##     integer f (server Diffie-Hellman public key)
    ##     string  signature
    ## For diffie-hellman-group-exchange-sha1 payload is:
    ##     string g (group generator)
    ##     string p (group prime)
    ##
    def ssh_KEX_DH_GEX_GROUP(self, packet):
        if self.kex_alg=="diffie-hellman-group1-sha1":
            # actually MSG_KEXDH_REPLY
            pub_key, packet=get_NS(packet, 1)
            f, packet=get_MP(packet)
            signature, packet=get_NS(packet, 1)
            self.debug("Server PK fingerprint: %s"%":".join([ch.encode("hex") for ch in md5(pub_key).digest()]))
            # Generate keys
            server_key = Key.from_string(pub_key)
            shared_secret = MPpow(f, self.x, DH_PRIME)
            h = sha1((NS(self.SSH_VERSION_STRING)+
                      NS(self.other_version_string)+
                      NS(self.our_kex_init_payload)+
                      NS(self.other_kex_init_payload)+
                      NS(pub_key)+
                      self.e+
                      MP(f)+
                      shared_secret))
            exchange_hash = h.digest()
            if not server_key.verify(signature, exchange_hash):
                self.send_disconnect(DISCONNECT_KEY_EXCHANGE_FAILED, "Bad signature")
                return
            self.key_setup(shared_secret, exchange_hash)
        else:
            self.p, rest = get_MP(packet)
            self.g, rest = get_MP(rest)
            self.x = self.generate_private_x(320)
            self.e = MPpow(self.g, self.x, self.p)
            self.send_packet(MSG_KEX_DH_GEX_INIT, self.e)
    
    ##
    ## MSG_NEWKEYS
    ## No payload
    ##
    def ssh_NEWKEYS(self, packet):
        if packet != "":
            self.send_disconnect(DISCONNECT_PROTOCOL_ERROR, "NEWKEYS takes no data")
            return
        if not self.next_transform.enc_block_size:
            return
        self.debug("Using new keys")
        self.transform = self.next_transform
        self.next_transform=None
        if self.out_compression_type == "zlib":
            self.out_compression = zlib.compressobj(6)
        if self.in_compression_type == "zlib":
            self.in_compression = zlib.decompressobj()
        if self.get_state()=="SSH_KEY_EXCHANGE":
            self.event("SSH_AUTH")
    
    ##
    ## MSG_SERVICE_ACCEPT
    ## Payload:
    ##     string service name
    ##
    def ssh_SERVICE_ACCEPT(self, packet):
        name, rest = get_NS(packet, 1)
        if name != self.requested_service_name:
            self.send_disconnect(DISCONNECT_PROTOCOL_ERROR,
                "received accept for service we did not request")
        self.debug("Starting service %s"%name)
        if self.get_state()=="SSH_AUTH":
            self.event("SSH_AUTH_PASSWORD")
        
    
    ##
    ## MSG_KEX_DH_GEX_REPLY
    ## Payload:
    ##     string   server host key
    ##     integer  server DH public key
    ##
    def ssh_KEX_DH_GEX_REPLY(self, packet):
        pub_key, packet = get_NS(packet)
        f, packet = get_MP(packet)
        signature, packet = get_NS(packet)
        self.debug("Server PK fingerprint: %s"%":".join([ch.encode("hex") for ch in md5(pub_key).digest()]))
        server_key = Key.from_string(pub_key)
        shared_secret = MPpow(f, self.x, self.p)
        h = sha1((
            NS(self.SSH_VERSION_STRING)+
            NS(self.other_version_string)+
            NS(self.our_kex_init_payload)+
            NS(self.other_kex_init_payload)+
            NS(pub_key)+
            "\x00\x00\x08\x00"+
            MP(self.p)+
            MP(self.g)+
            self.e+
            MP(f)+
            shared_secret))
        exchange_hash = h.digest()
        if not server_key.verify(signature, exchange_hash):
            self.send_disconnect(DISCONNECT_KEY_EXCHANGE_FAILED, "bad signature")
            return
        self.key_setup(shared_secret, exchange_hash)
    
    ##
    ## MSG_USERAUTH_FAILURE
    ## Payload:
    ##     string methods
    ##     byte partial success
    ##
    def ssh_USERAUTH_FAILURE(self, packet):
        methods, partial=get_NS(packet)
        partial=bool(ord(partial))
        if partial:
            self.debug("Authetication method '%s' has partial success. Trying next method (%s)"%(self.last_auth, methods))
        else:
            self.debug("Authentication method '%s' has been failed. Trying next method (%s)"%(self.last_auth, methods))
        
        self.debug("Partially authenticated with '%s'. Trying next method"%self.last_auth)
        self.authenticated_with.add(self.last_auth)
        methods_left=[x for x in [x.strip() for x in methods.split(",")] if x not in self.authenticated_with]
        if methods_left:
            # Try to authenticate other method
            self.authenticate(methods_left)
            return
        self.ssh_failure("Authentication failed")
    
    ##
    ## MSG_USERAUTH_SUCCESS
    ##
    def ssh_USERAUTH_SUCCESS(self, packet):
        self.event("SSH_CHANNEL")
    
    ##
    ## MSG_USERAUTH_MANNER
    ## Payload:
    ##     string message
    ##     string language
    ##
    def ssh_USERAUTH_BANNER(self, packet):
        message, language, rest = get_NS(packet, 2)
        self.motd=message
    
    ##
    ## MSG_USERAUTH_PK_OK
    ## Has different meanings depending on current authentication method.
    ## Try to dispatch
    ##
    def ssh_USERAUTH_PK_OK(self, packet):
        try:
            h=getattr(self, "ssh_USERAUTH_PK_OK_%s"%self.last_auth.lower().replace("-", "_"))
        except AttributeError:
            self.request_auth_none()
            return
        h(packet)
    
    ##
    ## MSG_USERAUTH_PK_OK
    ## publickey authentication
    ## Payload:
    ##     string pk algorithm
    ##     string pk blob
    ##
    def ssh_USERAUTH_PK_OK_publickey(self, packet):
        # Requesting to sign already signed authentication request.
        self.request_auth_none()
    
    ##
    ## MSG_USERAUTH_PK_OK
    ## keyboard-interactive authentication
    ## Payload:
    ##     string name
    ##     string instruction
    ##     string lang
    ##     string data
    ##
    def ssh_USERAUTH_PK_OK_keyboard_interactive(self, packet):
        name, instruction, lang, data = get_NS(packet, 3)
        n_prompts = struct.unpack('!L', data[:4])[0]
        data = data[4:]
        prompts=[]
        for i in range(n_prompts):
            s, data=get_NS(data, 1)
            prompts+=[(s, bool(ord(data[0])))]
            data=data[1:]
        responses=[self.access_profile.password]
        data=struct.pack("!L", len(responses))
        for r in responses:
            data += NS(r.encode("utf8"))
        self.send_packet(MSG_USERAUTH_INFO_RESPONSE, data)
    
    ##
    ## MSG_CHANNEL_OPEN_CONFIRMATION
    ## Payload:
    ##    uint32  local channel number
    ##    uint32  remote channel number
    ##    uint32  remote window size
    ##    uint32  remote maximum packet size
    ##    <channel specific data>
    ##
    def ssh_CHANNEL_OPEN_CONFIRMATION(self, packet):
        (local_channel, remote_channel,
            remote_window, remote_max_packet)=struct.unpack(">4L", packet[:16])
        self.local_to_remote_channel[local_channel]=remote_channel
        self.remote_to_local_channel[remote_channel]=local_channel
        self.remote_window_left=remote_window
        self.remote_max_packet=remote_max_packet
        self.current_remote_channel=remote_channel
        self.debug("Opening channel. local=%d remote=%d"%(local_channel, remote_channel))
        self.event("SSH_PTY")
    
    ##
    ## MSG_CHANNEL_OPEN_FAILURE
    ##
    def ssh_CHANNEL_OPEN_FAILURE(self, packet):
        self.ssh_failure("Cannot open channel")
    
    ##
    ## MSG_CHANNEL_WINDOW_ADJUST
    ## Payload:
    ##     uint32 local channel number
    ##     uint32 bytes to add
    ##
    def ssh_CHANNEL_WINDOW_ADJUST(self, packet):
        local_channel, bytes_to_add = struct.unpack(">2L", packet[:8])
        self.remote_window_left += bytes_to_add
        self.flush_data_buffer()
    
    ##
    ## MSG_CHANNEL_SUCCESS
    ##
    def ssh_CHANNEL_SUCCESS(self, packet):
        s=self.get_state()
        if s=="SSH_PTY":
            self.event("SSH_SHELL")
        elif s=="SSH_SHELL":
            self.is_ssh_ready=True
            self.event("START")
    
    ##
    ## MSG_CHANNEL_DATA
    ## Payload:
    ##    int    channel_id
    ##    string data
    ##
    def ssh_CHANNEL_DATA(self, packet):
        channel_id,=struct.unpack(">L", packet[:4]) # @todo: Check local channel id
        packet, rest=get_NS(packet[4:])
        CLI.on_read(self, packet)
        self.local_window_left -= len(packet)
        if self.local_window_left <= 0: # @todo: adaptive behavior
            self.local_window_left=self.local_window_size
            self.send_packet(MSG_CHANNEL_WINDOW_ADJUST,
                struct.pack(">2L", self.current_remote_channel, self.local_window_left)
            )
        #self.__flush_submitted_data()
    
    ##
    ## MSG_CHANNEL_EXTENDED_DATA
    ## Payload:
    ##     int    channel_id
    ##     int    data_type
    ##     string data
    ##
    def ssh_CHANNEL_EXTENDED_DATA(self, packet):
        channel_id, data_type=struct.unpack(">2L", packet[:4]) # @todo: Check local channel id
        packet, rest=get_NS(packet[8:])
        self.debug("Read extended: %r"%packet)
        self.feed(packet, cleanup=self.profile.cleaned_input)
        #self.__flush_submitted_data()
    
    ## Message dispatchers
    SSH_MESSAGES={
        MSG_DISCONNECT    : ssh_DISCONNECT,
        MSG_IGNORE        : ssh_IGNORE,
        MSG_UNIMPLEMENTED : ssh_UNIMPLEMENTED,
        MSG_DEBUG         : ssh_DEBUG,
        #MSG_SERVICE_REQUEST = 5
        MSG_SERVICE_ACCEPT : ssh_SERVICE_ACCEPT,
        MSG_KEXINIT        : ssh_KEXINIT,
        MSG_NEWKEYS        : ssh_NEWKEYS,
        #MSG_KEXDH_INIT = 30
        #MSG_KEXDH_REPLY = 31
        #MSG_KEX_DH_GEX_REQUEST_OLD = 30
        #MSG_KEX_DH_GEX_REQUEST = 34
        MSG_KEX_DH_GEX_GROUP : ssh_KEX_DH_GEX_GROUP,
        #MSG_KEX_DH_GEX_INIT = 32
        MSG_KEX_DH_GEX_REPLY : ssh_KEX_DH_GEX_REPLY,
        MSG_USERAUTH_FAILURE : ssh_USERAUTH_FAILURE,
        MSG_USERAUTH_SUCCESS : ssh_USERAUTH_SUCCESS,
        MSG_USERAUTH_BANNER  : ssh_USERAUTH_BANNER,
        MSG_USERAUTH_PK_OK   : ssh_USERAUTH_PK_OK,
        MSG_CHANNEL_DATA     : ssh_CHANNEL_DATA,
        MSG_CHANNEL_EXTENDED_DATA     : ssh_CHANNEL_EXTENDED_DATA,
        MSG_CHANNEL_OPEN_CONFIRMATION : ssh_CHANNEL_OPEN_CONFIRMATION,
        MSG_CHANNEL_OPEN_FAILURE      : ssh_CHANNEL_OPEN_FAILURE,
        MSG_CHANNEL_WINDOW_ADJUST     : ssh_CHANNEL_WINDOW_ADJUST,
        MSG_CHANNEL_SUCCESS           : ssh_CHANNEL_SUCCESS,
    }

# Diffie-Hellman primes from Oakley Group 2 [RFC 2409]
DH_PRIME = long("17976931348623159077083915679378745319786029604875601170644"
"442368419718021615851936894783379586492554150218056548598050364644054819923"
"910005079287700335581663922955313623907650873575991482257486257500742530207"
"744771258955095793777842444242661733472762929938766870920560605027081084290"
"7692932019128194467627007L")
DH_GENERATOR = 2L
