# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ASN.1 BER utitities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import math
import struct
# NOC modules
from noc.speedup.ber import parse_tlv_header, parse_p_oid


class DecodeError(Exception):
    pass


class BERDecoder(object):
    def parse_tlv(self, msg):
        tag_class, tag, is_primitive, is_implicit, offset, length = parse_tlv_header(msg)
        value, rest = msg[offset:offset + length], msg[offset + length:]
        if is_implicit:
            return self.parse_implicit(value, tag), rest
        try:
            decoder = self.DECODERS[tag_class][is_primitive][tag]
            return decoder(self, value), rest
        except KeyError:
            pt = "primitive" if is_primitive else "constructed"
            if is_implicit:
                pt = "implicit " + pt
            if tag_class:
                pt += " application"
            raise DecodeError(
                "Cannot find BER decoder for %s class %d (%X)" % (
                    pt, tag, tag))

    def parse_eoc(self, msg):
        return None

    def parse_boolean(self, msg):
        if not msg:
            return False
        return bool(ord(msg[0]))

    INT_MASK = {
        1: struct.Struct("!b"),
        2: struct.Struct("!h"),
        4: struct.Struct("!i"),
        8: struct.Struct("!q")
    }

    def parse_int(self, msg):
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
            v = (v << 8) + ord(c)
        if ord(msg[0]) & 0x80:
            # Negative number
            m = 1 << (8 * len(msg))
            v -= m
        return v

    def parse_real(self, msg):
        """
        """
        if not msg:
            return 0.0
        f = ord(msg[0])
        if f & 0x80:  # Binary encoding, 8.5.6
            # @todo: Снести в конец
            base = {
                0x00: 2,
                0x10: 4,
                0x20: 16
            }[f & 0x30]  # 8.5.6.2
            n = (f & 0x03) + 1
            e = self.parse_int(msg[1:n + 1])  # 8.5.6.4
            p = self.parse_int(msg[n + 1:])  # 8.5.6.5
            if f & 0x40:
                p = -p  # 8.5.6.1
            return p * pow(base, e)
        elif f & 0xc0 == 0:  # Decimal encoding, 8.5.7
            try:
                if f & 0x3f == 0x01:  # ISO 6093 NR1 form
                    return float(msg[1:])  # 456
                elif f & 0x3f == 0x02:  # ISO 6093 NR2 form
                    return float(msg[1:])  # 4.56
                elif f & 0x3f == 0x03:  # ISO 6093 NR3 form
                    return float(msg[1:])  # 0123e456
            except ValueError:
                raise DecodeError("Invalid REAL representation: %s" % msg[1:])
        elif f & 0x40:  # infinitive, 8.5.8
            return float("-inf" if f & 0x01 else "inf")
        else:
            raise DecodeError("Unknown REAL encoding: %s" % f)

    def parse_p_bitstring(self, msg):
        unused = ord(msg[0])
        r = "".join(BITSTING[ord(c)] for c in msg)
        if unused:
            r = r[:-unused]
        return r

    def parse_p_octetstring(self, msg):
        return msg

    def parse_c_octetstring(self, msg):
        r = []
        while msg:
            v, msg = self.parse_tlv(msg)
            r += [v]
        return r

    def parse_null(self, msg):
        return None

    def parse_a_ipaddress(self, msg):
        return "%d.%d.%d.%d" % (
            ord(msg[0]), ord(msg[1]), ord(msg[2]), ord(msg[3]))

    def parse_p_oid(self, msg):
        """
        >>> BERDecoder().parse_p_oid("+\\x06\\x01\\x02\\x01\\x01\\x05\\x00")
        "1.3.6.1.2.1.1.5.0"
        """
        self.last_oid = parse_p_oid(msg)
        return self.last_oid

    def parse_compressed_oid(self, msg):
        """
        :param msg:
        :return:
        """
        pos = ord(msg[0]) - 1
        parts = self.last_oid.split(".")[:pos] + [str(ord(d)) for d in msg[1:]]
        self.last_oid = ".".join(parts)
        return self.last_oid

    def parse_sequence(self, msg):
        r = []
        while msg:
            v, msg = self.parse_tlv(msg)
            r += [v]
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

    def parse_utctime(self, msg):
        return msg  # @todo: Convert to datetime

    DECODERS = {
        # Universal types
        0: {
            # Primitive types
            True: {
                0: parse_eoc,  # 0, 0, EOC (End-of-Content)
                1: parse_boolean,  # 1, 0x1, BOOLEAN
                2: parse_int,  # 2, 0x2, INTEGER
                3: parse_p_bitstring,  # 3, 0x3, BIT STRING
                4: parse_p_octetstring,  # 4, 0x4, OCTET STRING
                5: parse_null,  # 5, 0x5, NULL
                6: parse_p_oid,  # 6, 0x6, OBJECT IDENTIFIER
                # Object Descriptor	P/C	7	7
                # EXTERNAL	C	8	8
                9: parse_real,  # REAL (float)	P	9	9
                10: parse_int,  # 10, 0xA, ENUMERATED
                # UTF8String	P/C	12	C
                # RELATIVE-OID	P	13	D
                # NumericString	P/C	18	12
                # PrintableString	P/C	19	13
                # T61String	P/C	20	14
                # VideotexString	P/C	21	15
                # IA5String	P/C	22	16
                22: parse_utctime,  # 23, 0x17, UTCTime
                # GeneralizedTime	P/C	24	18
                # GraphicString	P/C	25	19
                # VisibleString	P/C	26	1A
                # GeneralString	P/C	27	1B
                # UniversalString	P/C	28	1C
                # CHARACTER STRING	P/C	29	1D
                # BMPString	P/C	30	1E
                # (use long-form)	-	31	1F
                0x80: parse_null,  # missed instance?
            },
            # Constructed types
            False: {
                # BIT STRING	P/C	3	3
                4: parse_c_octetstring,  # 4, 0x4, OCTET STRING
                6: parse_sequence,  # 6, 0x6, OBJECT IDENTIFIER
                # Object Descriptor	P/C	7	7
                7: parse_sequence,
                # EXTERNAL	C	8	8
                # EMBEDDED PDV	C	11	B
                # UTF8String	P/C	12	C
                16: parse_sequence,  # 10, 0x10, SEQUENCE and SEQUENCE OF
                17: parse_set,  # 17, 0x11, SET and SET OF
                # NumericString	P/C	18	12
                # PrintableString	P/C	19	13
                # T61String	P/C	20	14
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
            }
        },
        # SNMP application types
        64: {
            True: {
                0: parse_a_ipaddress,  # IpAddress
                1: parse_int,  # Counter32
                2: parse_int,  # Gauge32
                3: parse_int,  # TimeTicks
                4: parse_p_octetstring,  # Opaque
                # 5: NsapAddress
                6: parse_int,   # Counter64
                # 7: UInteger32
                # 14: Uncompressed delta identifier
                14: parse_p_oid,
                # 15: Compressed delta identifier
                15: parse_compressed_oid
            },
            False: {}
        }
    }


class BEREncoder(object):
    INF = float("inf")
    NINF = float("-inf")
    NAN = float("nan")
    MZERO = float("-0")

    struct_Q = struct.Struct("!Q")

    def encode_tlv(self, tag, primitive, data):
        # Encode tag
        t = tag
        t |= 0 if primitive else 0x20
        # Encode length
        l = len(data)
        if l < 0x80:
            # Short form
            return "%s%s%s" % (chr(t), chr(l), data)
        else:
            # Prepare length's representation
            ll = self.struct_Q.pack(l).lstrip("\x00")
            return "%s%s%s%s" % (chr(t), chr(0x80 | len(ll)), ll, data)

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
            data = "".join(data)
        return self.encode_tlv(16, False, data)

    def encode_choice(self, tag, data):
        if isinstance(data, (list, tuple)):
            data = "".join(data)
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
            return "\x02\x01\x00"
        elif data > 0:
            r = self.struct_Q.pack(data).lstrip("\x00")
            if r[0] >= "\x80":
                r = "\x00" + r
        elif data < 0:
            data = -data
            r = self.struct_Q.pack(data).lstrip("\x00")
            l = len(r)
            comp = 1 << (l * 8 - 1)
            if comp < data:
                comp <<= 8
            r = self.struct_Q.pack(comp - data).lstrip("\x00")
            if r:
                r = chr(ord(r[0]) | 0x80) + r[1:]
            else:
                r = "\x80" + "\x00" * (l - 1)
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
        return self.encode_tlv(
            9, True, "0x03%dE%s%d" % (m, "" if e else "+", e))

    def encode_null(self):
        return self.encode_tlv(5, True, "")

    def encode_oid(self, data):
        """
        >>> BEREncoder().encode_oid("1.3.6.1.2.1.1.5.0")
        '\\x06\\x08+\\x06\\x01\\x02\\x01\\x01\\x05\\x00'

        :param data:
        :return:
        """
        d = [int(x) for x in data.split(".")]
        r = [chr(d[0] * 40 + d[1])]
        for v in d[2:]:
            if v < 0x7f:
                r += [chr(v)]
            else:
                rr = []
                while v:
                    rr += [(v & 0x7f) | 0x80]
                    v >>= 7
                rr.reverse()
                rr[-1] &= 0x7f
                r += [chr(x) for x in rr]
        return self.encode_tlv(6, True, "".join(r))


def decode(msg):
    decoder = BERDecoder()
    data, _ = decoder.parse_tlv(msg)
    return data


# Calculate bitsting cache
# value -> string of bits
BITSTING = {}
for i in range(256):
    BITSTING[i] = "".join(
        "%d" % ((i >> j) & 1) for j in range(7, -1, -1))
