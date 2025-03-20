# ----------------------------------------------------------------------
# ASN.1 BER utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import math
import struct
import codecs

# Third-party modules
from typing import Tuple, Any, List, Optional

# NOC modules
from noc.core.comp import smart_bytes, smart_text
from gufo.noc.speedup import parse_tlv_header, parse_p_oid, encode_int, encode_oid
from noc.core.mib import mib


def did(tag_class: int, is_constructed: int, tag_id: int) -> int:
    """
    Calculate decoder_id as <tag id > | tag_class | constructed
    :param tag_class:
    :param is_constructed:
    :param tag_id:
    :return:
    """
    did = tag_class >> 5
    if is_constructed:
        did |= 1
    return did | (tag_id << 3)


class BERDecoder(object):
    def __init__(self, display_hints=None, include_raw=False):
        self.last_oid: Optional[str] = None
        self.oid_msg: Optional[bytes] = None
        self.raw_pdu: Optional[bytes] = None
        self.raw_varbinds: List[Tuple[str, Any, bytes]] = []
        self.display_hints = display_hints
        self.include_raw = include_raw

    @staticmethod
    def split_tlv(msg: bytes) -> Tuple[bytes, bytes]:
        decoder_id, tag_class, tag, is_constructed, is_implicit, offset, length = parse_tlv_header(
            msg
        )
        return msg[offset : offset + length], msg[offset + length :]

    def parse_tlv(self, msg: bytes) -> Tuple[Any, bytes]:
        decoder_id, tag_class, tag, is_constructed, is_implicit, offset, length = parse_tlv_header(
            msg
        )
        if self.include_raw and is_constructed and is_implicit:
            # Save pdu message
            self.raw_pdu = msg
        value, rest = msg[offset : offset + length], msg[offset + length :]
        if is_implicit:
            return self.parse_implicit(value, tag), rest
        try:
            type_dec = self.DECODERS[decoder_id]
            return type_dec(self, value), rest
        except KeyError:
            pt = "constructed" if is_constructed else "primitive"
            if is_implicit:
                pt = f"implicit {pt}"
            if tag_class:
                pt += f" application {tag_class}"
            raise ValueError(
                "Cannot find BER decoder for %s class %d (0x%X): %s"
                % (pt, tag, tag, codecs.encode(value, "hex").decode("utf-8"))
            )

    def parse_eoc(self, msg):
        return None

    def parse_boolean(self, msg: bytes) -> bool:
        if not msg:
            return False
        return bool(msg[0])

    INT_MASK = {
        1: struct.Struct("!b"),
        2: struct.Struct("!h"),
        4: struct.Struct("!i"),
        8: struct.Struct("!q"),
    }

    def parse_int(self, msg: bytes) -> int:
        """
        >>> BERDecoder().parse_int('')
        0
        >>> BERDecoder().parse_int('\\x00')
        0
        >>> BERDecoder().parse_int('\\x01')
        1
        >>> BERDecoder().parse_int('\\x7f')
        127
        >>> BERDecoder().parse_int('\\x00\\x80')
        128
        >>> BERDecoder().parse_int('\\x01\\x00')
        256
        >>> BERDecoder().parse_int('\\x80')
        -128
        >>> BERDecoder().parse_int('\\xff\\x7f')
        -129

        :param msg:
        :return: integer
        """
        if not msg:
            return 0
        # Try to speedup
        mask = self.INT_MASK.get(len(msg))
        if mask:
            return mask.unpack(msg)[0]
        # Decode as is
        v = 0
        for c in msg:
            v = (v << 8) + c
        if msg[0] & 0x80:
            # Negative number
            m = 1 << (8 * len(msg))
            v -= m
        return v

    def parse_real(self, msg: bytes) -> float:
        if not msg:
            return 0.0
        f = msg[0]
        if f & 0x80:  # Binary encoding, 8.5.6
            # @todo: Снести в конец
            base = {0x00: 2, 0x10: 4, 0x20: 16}[f & 0x30]  # 8.5.6.2
            n = (f & 0x03) + 1
            e = self.parse_int(msg[1 : n + 1])  # 8.5.6.4
            p = self.parse_int(msg[n + 1 :])  # 8.5.6.5
            if f & 0x40:
                p = -p  # 8.5.6.1
            return p * pow(base, e)
        elif f & 0xC0 == 0:  # Decimal encoding, 8.5.7
            try:
                if f & 0x3F == 0x01:  # ISO 6093 NR1 form
                    return float(msg[1:])  # 456
                elif f & 0x3F == 0x02:  # ISO 6093 NR2 form
                    return float(msg[1:])  # 4.56
                elif f & 0x3F == 0x03:  # ISO 6093 NR3 form
                    return float(msg[1:])  # 0123e456
            except ValueError:
                raise ValueError("Invalid REAL representation: %s" % msg[1:])
        elif f & 0x40:  # infinitive, 8.5.8
            return float("-inf" if f & 0x01 else "inf")
        else:
            raise ValueError("Unknown REAL encoding: %s" % f)

    def parse_p_bitstring(self, msg: bytes) -> bytes:
        unused = msg[0]
        r = b"".join(BITSTING[c] for c in msg)
        if unused:
            r = r[:-unused]
        return r

    def parse_p_octetstring(self, msg: bytes) -> str:
        if self.last_oid:
            return mib.render(self.last_oid, msg, self.display_hints)
        return msg

    def parse_p_t61_string(self, msg: bytes) -> str:
        return smart_text(msg, errors="ignore")

    def parse_c_octetstring(self, msg: bytes) -> List[str]:
        r = []
        while msg:
            v, msg = self.parse_tlv(msg)
            r += [smart_text(v, errors="ignore")]
        return r

    def parse_c_t61_string(self, msg):
        r = []
        while msg:
            v, msg = self.parse_tlv(msg)
            r += [v]
        return r

    def parse_null(self, msg: bytes) -> None:
        return None

    def parse_a_ipaddress(self, msg: bytes) -> str:
        if not msg:
            raise ValueError("Invalid IP Address: '%s'" % msg.encode("hex"))
        return "%d.%d.%d.%d" % (msg[0], msg[1], msg[2], msg[3])

    def parse_p_oid(self, msg: bytes) -> str:
        """
        >>> BERDecoder().parse_p_oid("+\\x06\\x01\\x02\\x01\\x01\\x05\\x00")
        "1.3.6.1.2.1.1.5.0"
        """
        self.last_oid = smart_text(parse_p_oid(msg))
        return self.last_oid

    def parse_compressed_oid(self, msg: bytes) -> str:
        """
        :param msg:
        :return:
        """
        pos = msg[0] - 1
        parts = self.last_oid.split(".")[:pos] + [str(d) for d in msg[1:]]
        self.last_oid = ".".join(parts)
        return smart_text(self.last_oid)

    def parse_sequence(self, msg):
        r = []
        while msg:
            v, msg = self.parse_tlv(msg)
            if self.include_raw and self.last_oid == v:
                self.oid_msg = msg
            r.append(v)
        if self.include_raw and not msg and len(r) == 2:
            # last value
            self.raw_varbinds.append((self.last_oid, r[-1], self.oid_msg))
        return r

    def parse_implicit(self, msg, tag):
        r = [tag]
        while msg:
            v, msg = self.parse_tlv(msg)
            r += [v]
        return r

    def parse_set(self, msg):
        r = []
        while msg:
            v, msg = self.parse_tlv(msg)
            r += [v]
        return r

    def parse_opaque(self, msg):
        return self.parse_tlv(msg)[0]

    def parse_utctime(self, msg):
        return msg  # @todo: Convert to datetime

    def parse_float(self, msg):
        """
        ANSI/IEEE Std 754-1985 binary floating point
        :param msg:
        :return:
        """
        return struct.unpack("!f", msg)[0]

    def parse_double(self, msg):
        """
        ANSI/IEEE Std 754-1985 binary floating point
        :param msg:
        :return:
        """
        return struct.unpack("!d", msg)[0]

    DECODERS = {
        # > Universal types
        # >> Universal, Primitive types
        did(0, False, 0): parse_eoc,  # 0, 0, EOC (End-of-Content)
        did(0, False, 1): parse_boolean,  # 1, 0x1, BOOLEAN
        did(0, False, 2): parse_int,  # 2, 0x2, INTEGER
        did(0, False, 3): parse_p_bitstring,  # 3, 0x3, BIT STRING
        did(0, False, 4): parse_p_octetstring,  # 4, 0x4, OCTET STRING
        did(0, False, 5): parse_null,  # 5, 0x5, NULL
        did(0, False, 6): parse_p_oid,  # 6, 0x6, OBJECT IDENTIFIER
        # Object Descriptor	P/C	7	7
        # EXTERNAL	C	8	8
        did(0, False, 9): parse_real,  # REAL (float)	P	9	9
        did(0, False, 10): parse_int,  # 10, 0xA, ENUMERATED
        # UTF8String	P/C	12	C
        # RELATIVE-OID	P	13	D
        # NumericString	P/C	18	12
        # PrintableString	P/C	19	13
        did(0, False, 20): parse_p_t61_string,  # T61String	P/C	20	14
        # VideotexString	P/C	21	15
        # IA5String	P/C	22	16
        did(0, False, 23): parse_utctime,  # 23, 0x17, UTCTime
        # GeneralizedTime	P/C	24	18
        # GraphicString	P/C	25	19
        # VisibleString	P/C	26	1A
        # GeneralString	P/C	27	1B
        # UniversalString	P/C	28	1C
        # CHARACTER STRING	P/C	29	1D
        # BMPString	P/C	30	1E
        # (use long-form)	-	31	1F
        # SNMP_NOSUCHOBJECT 0x80
        # SNMP_NOSUCHINSTANCE 0x81
        # SNMP_ENDOFMIBVIEW 0x82
        did(0, False, 0x80): parse_null,  # missed instance?
        # >> Universal, Constructed types
        # BIT STRING	P/C	3	3
        did(0, True, 4): parse_c_octetstring,  # 4, 0x4, OCTET STRING
        did(0, True, 6): parse_sequence,  # 6, 0x6, OBJECT IDENTIFIER
        # Object Descriptor	P/C	7	7
        did(0, True, 7): parse_sequence,
        # EXTERNAL	C	8	8
        # EMBEDDED PDV	C	11	B
        # UTF8String	P/C	12	C
        did(0, True, 16): parse_sequence,  # 16, 0x10, SEQUENCE and SEQUENCE OF
        did(0, True, 17): parse_set,  # 17, 0x11, SET and SET OF
        # NumericString	P/C	18	12
        # PrintableString	P/C	19	13
        did(0, True, 20): parse_c_t61_string,  # T61String	P/C	20	14
        # VideotexString	P/C	21	15
        # IA5String	P/C	22	16
        # UTCTime	P/C	23	17
        # GeneralizedTime	P/C	24	18
        # GraphicString	P/C	25	19
        # VisibleString	P/C	26	1A
        # GeneralString	P/C	27	1B
        # UniversalString	P/C	28	1C
        # CHARACTER STRING	P/C	29	1D
        # BMPString	P/C	30	1E
        # (use long-form)	-	31	1F
        # > SNMP application types
        # >> SNMP, Primitive types
        did(64, False, 0): parse_a_ipaddress,  # IpAddress
        did(64, False, 1): parse_int,  # Counter32
        did(64, False, 2): parse_int,  # Gauge32
        did(64, False, 3): parse_int,  # TimeTicks
        did(64, False, 4): parse_opaque,  # Opaque
        # 5: NsapAddress
        did(64, False, 6): parse_int,  # 6, Counter64
        # 7: UInteger32
        did(64, False, 14): parse_p_oid,  # 14: Uncompressed delta identifier
        did(64, False, 15): parse_compressed_oid,  # 15: Compressed delta identifier
        # SNMP Float types
        did(128, False, 120): parse_float,
        did(128, False, 121): parse_double,
    }


class BEREncoder(object):
    INF = float("inf")
    NINF = float("-inf")
    NAN = float("nan")
    MZERO = float("-0")

    struct_Q = struct.Struct("!Q")
    struct_B = struct.Struct("B")
    struct_BB = struct.Struct("BB")

    def encode_tlv(self, tag: int, primitive: bool, data: bytes) -> bytes:
        data = smart_bytes(data)
        # Encode tag
        t = tag
        if not primitive:
            t |= 0x20
        # Encode length
        ln = len(data)
        if ln < 0x80:
            # Short form
            return self.struct_BB.pack(t, ln) + data
        # Prepare length's representation
        ll = self.struct_Q.pack(ln).lstrip(b"\x00")
        return self.struct_BB.pack(t, 0x80 | len(ll)) + ll + data

    def encode_octet_string(self, data):
        """
        >>> BEREncoder().encode_octet_string("test")
        '\\x04\\x04test'
        >>> BEREncoder().encode_octet_string("public")
        '\\x04\\x06public'
        >>> BEREncoder().encode_octet_string("")
        '\\x04\\x00'

        :param data:
        :return:
        """
        return self.encode_tlv(4, True, data)

    def encode_sequence(self, data):
        if isinstance(data, (list, tuple)):
            data = b"".join(data)
        return self.encode_tlv(16, False, data)

    def encode_choice(self, tag, data):
        if isinstance(data, (list, tuple)):
            data = b"".join(data)
        return self.encode_tlv(0x80 + tag, False, data)

    def encode_int(self, data):
        """
        >>> BEREncoder().encode_int(0)
        '\\x02\\x01\\x00'
        >>> BEREncoder().encode_int(1)
        '\\x02\\x01\\x01'
        >>> BEREncoder().encode_int(127)
        '\\x02\\x01\\x7f'
        >>> BEREncoder().encode_int(128)
        '\\x02\\x02\\x00\\x80'
        >>> BEREncoder().encode_int(256)
        '\\x02\\x02\\x01\\x00'
        >>> BEREncoder().encode_int(-128)
        '\\x02\\x01\\x80'
        >>> BEREncoder().encode_int(-129)
        '\\x02\\x02\\xff\\x7f'
        """
        if data == 0:
            return b"\x02\x01\x00"
        if data > 0:
            return encode_int(data)
        data = -data
        r = self.struct_Q.pack(data).lstrip(b"\x00")
        ln = len(r)
        comp = 1 << (ln * 8 - 1)
        if comp < data:
            comp <<= 8
        r = self.struct_Q.pack(comp - data).lstrip(b"\x00")
        if r:
            r = self.struct_B.pack(r[0] | 0x80) + r[1:]
        else:
            r = b"\x80" + b"\x00" * (ln - 1)
        return self.encode_tlv(2, True, r)

    def encode_real(self, data):
        """
        >>> BEREncoder().encode_real(float("+inf"))
        '\\t\\x01@'
        >>> BEREncoder().encode_real(float("-inf"))
        '\\t\\x01A'
        >>> BEREncoder().encode_real(float("nan"))
        '\\t\\x01B'
        >>> BEREncoder().encode_real(float("-0"))
        '\\t\\x01C'
        >>> BEREncoder().encode_real(float("1"))
        '\\t\\x080x031E+0'
        >>> BEREncoder().encode_real(float("1.5"))
        '\\t\\t0x0315E-1'

        :param data:
        :return:
        """
        if data == self.INF:
            return self.encode_tlv(9, True, "\x40")
        elif data == self.NINF:
            return self.encode_tlv(9, True, "\x41")
        elif math.isnan(data):
            return self.encode_tlv(9, True, "\x42")
        elif data == self.MZERO:
            return self.encode_tlv(9, True, "\x43")
        # Normalize
        e = 0
        m = data
        while int(m) != m:
            e -= 1
            m *= 10
        m = int(m)
        while m and m % 10 == 0:
            m /= 10
            e += 1
        return self.encode_tlv(9, True, "0x03%dE%s%d" % (m, "" if e else "+", e))

    def encode_null(self) -> bytes:
        """
        05 00
        :return:
        """
        return b"\x05\x00"

    def encode_oid(self, data: str) -> bytes:
        """
        >>> BEREncoder().encode_oid("1.3.6.1.2.1.1.5.0")
        '\\x06\\x08+\\x06\\x01\\x02\\x01\\x01\\x05\\x00'

        :param data:
        :return:
        """
        return encode_oid(smart_bytes(data))


# Internal state, singleton is not possible
# decoder = BERDecoder()
# No state, singleton is possible
encoder = BEREncoder()


def decode(
    msg: bytes, include_raw: bool = False
) -> Tuple[Tuple[int, bytes, List[Any]], Optional[bytes], List[Tuple[str, Any, bytes]]]:
    decoder = BERDecoder(include_raw=include_raw)
    data, _ = decoder.parse_tlv(msg)
    return data, decoder.raw_pdu, decoder.raw_varbinds


# Calculate bitsting cache
# value -> string of bits
BITSTING = {}
for i in range(256):
    BITSTING[i] = b"".join(b"%d" % ((i >> j) & 1) for j in range(7, -1, -1))
