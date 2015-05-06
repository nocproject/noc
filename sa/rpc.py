# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SAE RPC Protocol
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import struct
import logging
import random
import time
import hashlib
import zlib
import logging
## Third-party modules
from Crypto.Cipher import XOR
## NOC modules
from noc.sa.protocols.sae_pb2 import Message, Error
from google.protobuf.service import RpcController
from noc.sa.protocols.sae_pb2 import *
from noc.lib.nbsocket import Protocol
from noc.lib.debug import error_report
from noc.sa.script.ssh.util import secure_random, bytes_to_long, long_to_bytes

PROTOCOL_NAME = "NOC SAE PROTOCOL (http://nocproject.org/)"
PROTOCOL_VERSION = "1.0"

# Oakley group 2
DH_PRIME = long("17976931348623159077083915679378745319786029604875601170644"
                "442368419718021615851936894783379586492554150218056548598050364644054819923"
                "910005079287700335581663922955313623907650873575991482257486257500742530207"
                "744771258955095793777842444242661733472762929938766870920560605027081084290"
                "7692932019128194467627007L")
DH_GENERATOR = 2L

## Crypto sessions
KEY_EXCHANGES = ["diffie-hellman-group1-sha1"]
PUBLIC_KEYS = ["ssh-dss"]
CIPHERS = ["aes256-cbc", "blowfish-cbc", "3des-cbc"]
MACS = ["hmac-sha1", "hmac-md5"]
COMPRESSIONS = ["zlib"]

CIPHER_MAP = {
    "aes256-cbc": ("AES", 32),
    "blowfish-cbc": ("Blowfish", 16),
    "3des-cbc": ("DES3", 24),
}

MAC_MAP = {
    "hmac-sha1": hashlib.sha1,
    "hmac-md5": hashlib.md5
}


class Controller(RpcController):
    """RPC Controller"""
    def __init__(self, stream):
        RpcController.__init__(self)
        self.stream = stream
        self.transaction = None

    def Reset(self):
        pass

    def Failed(self):
        pass

    def ErrorText(self):
        pass

    def StartCancel(self):
        pass

    def SetFailed(self, reason):
        pass

    def IsCancelled(self):
        pass

    def NotifyOnCancel(self, callback):
        pass


class Transaction(object):
    """Transaction data structure"""
    def __init__(self, factory, id, method=None, callback=None):
        logging.debug("Creating transaction id=%s method=%s callback=%s" % (
            id, method, callback))
        self.factory = factory
        self.id = id
        self.method = method
        self.callback = callback

    def commit(self, response=None, error=None):
        if self.callback:
            self.callback(self, response, error)
        self.factory.delete_transaction(self.id)

    def rollback(self, error):
        self.commit(error=error)


class TransactionFactory(object):
    """Transaction factory and storage"""
    def __init__(self):
        self.transactions = {}

    def __len__(self):
        return len(self.transactions)

    def __get_id(self):
        """Generate unique transaction id"""
        while True:
            id = random.randint(0, 0x7FFFFFFF)
            if id not in self.transactions:
                return id

    def __contains__(self, id):
        return id in self.transactions

    def __getitem__(self, id):
        return self.transactions[id]

    def begin(self, id=None, method=None, callback=None):
        """
        Begin transaction, remember callback and return transaction id
        """
        if id:
            if id in self.transactions:
                raise Exception("Transaction is already exists")
        else:
            id = self.__get_id()
        t = Transaction(self, id, method, callback)
        self.transactions[id] = t
        return t

    def delete_transaction(self, id):
        del self.transactions[id]

    def rollback_all_transactions(self, error):
        logging.debug("Rolling back all active transactions")
        for t in self.transactions.values():
            t.rollback(error)


class RPCProtocol(Protocol):
    """
    RPC Protocol PDU parser
    """
    def __init__(self, *args, **kwargs):
        super(RPCProtocol, self).__init__(*args, **kwargs)
        self.compression = None
        self.cipher = None
        self.mac = None

    def parse_pdu(self):
        """
        Parse PDUs of <len><data>
        Where <len> - unsigned 32-bit length in network order
        and <data> - is an arbitrary stream of <len> octets
        """
        r = []
        while len(self.in_buffer) >= 4:
            l = struct.unpack("!L", self.in_buffer[:4])[0]
            if len(self.in_buffer) >= 4 + l:
                r += [self.in_buffer[4:4 + l]]
                self.in_buffer = self.in_buffer[4 + l:]
            else:
                break
        return r


class Transform(object):
    def __init__(self, key_exhange, public_key, cipher, mac, compression):
        self.key_exhange = key_exhange
        self.public_key = public_key
        self.cipher = cipher
        self.mac = mac
        self.compression = compression
        if self.mac == "hmac-md5":
            self.hash = hashlib.md5
        elif self.mac == "hmac-sha1":
            self.hash = hashlib.sha1
        else:
            self.hash = None
        self.signature_size = self.hash().digest_size if self.hash else 0

        self.block_size = 0
        self.encrypt = None
        self.decrypt = None
        self.compress = None
        self.decompress = None

    def get_kex_request(self):
        """
        Get KEXRequest
        """
        logging.info("Beginning %s key exchange" % self.key_exhange)
        if self.key_exhange == "diffie-hellman-group1-sha1":
            self.x = generate_private_x(512)
            self.e = pow(DH_GENERATOR, self.x, DH_PRIME)
            r = KEXRequest()
            r.dh_group1_sha1.e = long_to_bytes(self.e)
        else:
            raise ValueError("Unsupported key exchange: %s" % self.key_exhange)
        self.kex_request = r.SerializeToString()
        return r

    def get_kex_response(self, request):
        """
        Get KEXResponse
        """
        logging.info("Negotiating %s key exchange" % self.key_exhange)
        self.kex_request = request.SerializeToString()
        if self.key_exhange == "diffie-hellman-group1-sha1":
            self.x = generate_private_x(512)
            self.e = pow(DH_GENERATOR, self.x, DH_PRIME)
            shared_secret = pow(bytes_to_long(request.dh_group1_sha1.e),
                                  self.x, DH_PRIME)
            r = KEXResponse()
            r.dh_group1_sha1.e = long_to_bytes(self.e)
        else:
            raise ValueError("Unsupported key exchange: %s" % self.key_exhange)
        self.kex_response = r.SerializeToString()
        self.set_key(shared_secret, self.get_exchange_hash(shared_secret),
                     server=True)
        return r

    def process_kex_response(self, response):
        """
        Complete KEX Process
        """
        logging.info("Completing %s key exchange" % self.key_exhange)
        self.kex_response = response.SerializeToString()
        if self.key_exhange == "diffie-hellman-group1-sha1":
            shared_secret = pow(bytes_to_long(response.dh_group1_sha1.e),
                                  self.x, DH_PRIME)
        else:
            raise ValueError("Unsupported key exchange: %s" % self.key_exhange)
        self.set_key(shared_secret, self.get_exchange_hash(shared_secret))

    def get_exchange_hash(self, shared_secret):
        """Calculate exchange hash"""
        return self.hash((
            PROTOCOL_NAME +
            PROTOCOL_VERSION +
            self.kex_request +
            self.kex_response +
            str(shared_secret)
        )).digest()

    def set_key(self, shared_secret, exchange_hash, server=False):
        def get_cipher(cipher, IV, key):
            m_name, key_size = CIPHER_MAP[cipher]
            m = __import__("Crypto.Cipher.%s" % m_name, {}, {}, "x")
            return m.new(key[:key_size], m.MODE_CBC, IV[:m.block_size])

        def get_key(c, shared_secret, exchange_hash):
            shared_secret = str(shared_secret)
            # @todo: add session_id
            k1 = self.hash(shared_secret + exchange_hash + c).digest()
            k2 = self.hash(shared_secret + exchange_hash + k1).digest()
            return k1 + k2
        
        def get_mac(key):
            ds = self.signature_size
            key = key[:ds] + "\x00" * (64 - ds)
            i = XOR.new("\x36").encrypt(key)
            o = XOR.new("\x5c").encrypt(key)
            return i, o

        logging.debug("Setting encryption key")
        IV_CS = get_key("A", shared_secret, exchange_hash)
        IV_SC = get_key("B", shared_secret, exchange_hash)
        enc_key_CS = get_key("C", shared_secret, exchange_hash)
        enc_key_SC = get_key("D", shared_secret, exchange_hash)
        integ_key_CS = get_key("E", shared_secret, exchange_hash)
        integ_key_SC = get_key("F", shared_secret, exchange_hash)

        if server:
            # Server -> Client
            self.encrypt = get_cipher(self.cipher, IV_SC, enc_key_SC).encrypt
            self.decrypt = get_cipher(self.cipher, IV_CS, enc_key_CS).decrypt
            self.i_mac = get_mac(integ_key_CS)
            self.o_mac = get_mac(integ_key_SC)
        else:
            # Client -> Server
            self.encrypt = get_cipher(self.cipher, IV_CS, enc_key_CS).encrypt
            self.decrypt = get_cipher(self.cipher, IV_SC, enc_key_SC).decrypt
            self.i_mac = get_mac(integ_key_SC)
            self.o_mac = get_mac(integ_key_CS)
        # Get block size
        m_name, key_size = CIPHER_MAP[self.cipher]
        m = __import__("Crypto.Cipher.%s" % m_name, {}, {}, "x")
        self.block_size = m.block_size

    def sign(self, seq_id, data):
        """
        Sign portion of data. Returns signature
        """
        data = struct.pack(">L", seq_id) + data
        i, o = self.o_mac
        inner = self.hash(i + data).digest()
        outer = self.hash(o + inner).digest()
        return outer

    def verify(self, seq_id, data, signature):
        """
        Check data is signed properly
        """
        data = struct.pack(">L", seq_id) + data
        i, o = self.i_mac
        inner = self.hash(i + data).digest()
        outer = self.hash(o + inner).digest()
        return outer == signature


class RPCSocket(object):
    """
    RPC Socket
    """
    protocol_class = RPCProtocol

    def __init__(self, service):
        self.service = service
        self.proxy = Proxy(self, SAEService_Stub)
        self.transactions = TransactionFactory()
        self.stat_rpc_requests = 0
        self.stat_rpc_responses = 0
        self.stat_rpc_errors = 0
        self.current_transform = Transform(None, None, None, None, None)
        self.next_transform = Transform(None, None, None, None, None)

    def set_next_transform(self, key_exhange, public_key, cipher,
                           mac, compression):
        def c(s):
            if s == "none":
                return None
            else:
                return s

        logging.debug("Setting next transform to %s" % ", ".join([
            key_exhange, public_key, cipher, mac, compression]))
        self.next_transform = Transform(c(key_exhange), c(public_key),
                                        c(cipher), c(mac), c(compression))

    def activate_next_transform(self):
        logging.debug("Activating next crypto transform")
        self.current_transform = self.next_transform
        self.next_transform = Transform(None, None, None, None, None)

    def start_kex(self, callback):
        """
        Begin key exchange
        """
        r = self.next_transform.get_kex_request()
        self.proxy.kex(r, callback)

    def get_kex_response(self, request):
        """
        Process KEX request and return KEX response or Error
        """
        return self.next_transform.get_kex_response(request)

    def complete_kex(self, response):
        """
        Complete KEX process by parsing response
        """
        return self.next_transform.process_kex_response(response)

    def on_read(self, data):
        # Check integrity when encryption is set
        if self.current_transform.signature_size:
            signature = data[-self.current_transform.signature_size:]
            data = data[:-self.current_transform.signature_size]
            # @todo: use sequence id
            if not self.current_transform.verify(0, data, signature):
                logging.error("Message integrity failure")
                self.close()
                return
        # Decrypt when encryption is set
        if self.current_transform.decrypt:
            data = self.current_transform.decrypt(data)
            # Strip padding
            pad_len, = struct.unpack("B", data[0])
            data = data[1:-pad_len]
        # Decompress data when compression is set
        if self.current_transform.decompress:
            data = self.current_transform.decompress(data)
        # Parse message
        msg = Message()
        msg.ParseFromString(data)
        # Process message
        # logging.debug("rpc_handle_message:\n%s" % msg)
        if msg.error.ByteSize():
            self.stat_rpc_errors += 1
            self.rpc_handle_error(msg.id, msg.error)
        elif msg.request.ByteSize():
            self.stat_rpc_requests += 1
            self.rpc_handle_request(msg.id, msg.request)
        elif msg.response.ByteSize():
            self.stat_rpc_responses += 1
            self.rpc_handle_response(msg.id, msg.response)

    def rpc_handle_request(self, id, request):
        logging.debug("rpc_handle_request: %s" % request.method)
        if id in self.transactions:
            self.send_error(id, ERR_TRANSACTION_EXISTS,
                            "Transaction %s is already exists" % id)
            return
        method = self.service.GetDescriptor().FindMethodByName(request.method)
        if method:
            req = self.service.GetRequestClass(method)()
            req.ParseFromString(request.serialized_request)
            # logging.debug("Request accepted:\nid: %s\n%s" % (id, str(req)))
            controller = Controller(self)
            controller.transaction = self.transactions.begin(id=id,
                                                        method=request.method)
            try:
                self.service.CallMethod(method, controller,
                                        req, self.send_response)
            except:
                self.send_error(id, ERR_INTERNAL,
                                "RPC Call to %s failed" % request.method)
                error_report()
        else:
            self.send_error(id, ERR_INVALID_METHOD,
                            "Invalid method '%s'" % request.method)

    def rpc_handle_response(self, id, response):
        # logging.debug("rpc_handle_response:\nid: %s\n%s" % (id, str(response)))
        if id not in self.transactions:
            logging.error("Invalid transaction: %s" % id)
            return
        t = self.transactions[id]
        method = self.service.GetDescriptor().FindMethodByName(t.method)
        if method:
            res = self.service.GetResponseClass(method)()
            res.ParseFromString(response.serialized_response)
            t.commit(response=res)
        else:
            logging.error("Invalid method: %s" % t.method)
            t.rollback()

    def rpc_handle_error(self, id, error):
        logging.debug("rpc_handle_error:\nid: %s\n%s" % (id, str(error)))
        if id not in self.transactions:
            logging.error("Invalid transaction: %s" % id)
            return
        self.transactions[id].commit(id, error=error)

    # Format and write SAE RPC PDU
    def write_message(self, msg):
        #s=zlib.compress(msg.SerializeToString())
        s = msg.SerializeToString()
        # Compress when compression is set
        if self.current_transform.compress:
            s = self.current_transform.compress(s)
        # Encrypt when encryption is set
        if self.current_transform.encrypt:
            # Pad to block size
            ls = len(s)
            bs = self.current_transform.block_size
            pad_len = bs - (len(s) + 1) % bs
            if pad_len == 0:
                pad_len = bs
            s = struct.pack("B", pad_len) + s + secure_random(pad_len)
            # Encrypt
            s = self.current_transform.encrypt(s)
        # Sign when encryption is set
        if self.current_transform.signature_size:
            s += self.current_transform.sign(0, s)  # @todo: sequence id
        # Write to socket
        self.write(struct.pack("!L", len(s)) + s)

    def send_request(self, id, method, request):
        logging.debug("send_request\nmethod: %s\n%s" % (method, str(request)))
        m = Message()
        m.id = id
        m.request.method = method
        m.request.serialized_request = request.SerializeToString()
        self.write_message(m)
        return id

    def send_response(self, controller, response=None, error=None):
        id = controller.transaction.id
        # logging.debug("send_response:\nid: %d\nresponse:\n%s\nerror:\n%s" % (
        #                id, str(response), str(error)))
        if id not in self.transactions:
            raise Exception("Invalid transaction")
        m = Message()
        m.id = id
        if error:
            m.error.code = error.code
            m.error.text = error.text
        if response:
            m.response.serialized_response = response.SerializeToString()
        self.write_message(m)
        controller.transaction.commit()

    def send_error(self, id, code, text):
        logging.debug("send_error:\nid: %s\ncode: %s\ntext: %s" % (id, code,
                                                                   text))
        m = Message()
        m.id = id
        m.error.code = code
        m.error.text = text
        self.write_message(m)

    def call(self, method, request, callback):
        t = self.transactions.begin(method=method, callback=callback)
        self.send_request(t.id, method, request)
        return t

    @property
    def stats(self):
        return [
            ("rpc.requests",  self.stat_rpc_requests),
            ("rpc.responses", self.stat_rpc_responses),
            ("rpc.errors",    self.stat_rpc_errors),
        ]


class Proxy(object):
    """
    Proxy class for RPC interface
    """
    def __init__(self, stream, stub_class):
        self.stream = stream
        self.stub = stub_class(stream.service)

    def __getattr__(self, name):
        return lambda request, callback: self.stream.call(name, request, callback)


def file_hash(path):
    """
    Calculate file hash for software update service
    """
    f = open(path)
    data = f.read()
    f.close()
    return hashlib.sha1(data).hexdigest()


def H(s):
    """
    Generic hash for digest authentication
    """
    return hashlib.sha1(s).hexdigest()


def get_nonce():
    """
    Generate random nonce for digest authentication

    @todo: use safe_random
    """
    ur = random.SystemRandom()
    return H(H(str(ur.random())[2:]) + str(ur.random())[2:])


def get_digest(name, password, nonce):
    """
    Compute digest for Activator authentication
    """
    return H(H(name + ":" + password) + ":" + nonce)


def generate_private_x(bits):
    """
    Generate random long of bits size
    """
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
