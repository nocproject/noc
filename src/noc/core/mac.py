# ----------------------------------------------------------------------
# MAC address manipulation routines
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re


# Regular expressions

# Cisco-like AABB.CCDD.EEFF
rx_mac_address_cisco = re.compile(r"^[0-9A-F]{4}(?P<sep>[.\-])[0-9A-F]{4}(?P=sep)[0-9A-F]{4}$")
# Alternative Cisco form 01AA.BBCC.DDEE.FF
rx_mac_address_cisco_media = re.compile(r"^01[0-9A-F]{2}\.[0-9A-F]{4}\.[0-9A-F]{4}\.[0-9A-F]{2}$")
# Size blocks, leading zeroes can be ommited
# AA:BB:C:DD:EE:F
rx_mac_address_sixblock = re.compile(
    r"^([0-9A-F]{1,2}):([0-9A-F]{1,2}):([0-9A-F]{1,2}):([0-9A-F]{1,2}):([0-9A-F]{1,2}):([0-9A-F]{1,2})$"
)
# HP-like AABBCC-DDEEFF
rx_mac_address_hp = re.compile(r"^[0-9A-F]{6}-[0-9A-F]{6}$")
# Unseparated block
rx_mac_address_solid = re.compile(r"^[0-9A-F]{12}$")

INPUT_TYPES = int | bytes | str


class MAC(str):
    """
    MAC address validation and conversion class

    >>> MAC("1234.5678.9ABC")
    '12:34:56:78:9A:BC'
    >>> MAC("1234.5678.9abc")
    '12:34:56:78:9A:BC'
    >>> MAC("0112.3456.789a.bc")
    '12:34:56:78:9A:BC'
    >>> MAC("1234.5678.9abc.def0")
    Traceback (most recent call last):
        ...
    ValueError: Invalid MAC: '1234.5678.9abc.def0'
    >>> MAC("12:34:56:78:9A:BC")
    '12:34:56:78:9A:BC'
    >>> MAC("12-34-56-78-9A-BC")
    '12:34:56:78:9A:BC'
    >>> MAC("0:13:46:50:87:5")
    '00:13:46:50:87:05'
    >>> MAC("123456-789abc")
    '12:34:56:78:9A:BC'
    >>> MAC("12-34-56-78-9A-BC-DE")   #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: Invalid MAC: '12:34:56:78:9A:BC:DE'
    >>> MAC("AB-CD-EF-GH-HJ-KL")   #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: Invalid MAC: 'AB:CD:EF:GH:HJ:KL'
    >>> MAC("aabb-ccdd-eeff")
    'AA:BB:CC:DD:EE:FF'
    >>> MAC("aabbccddeeff")
    'AA:BB:CC:DD:EE:FF'
    >>> MAC("AABBCCDDEEFF")
    'AA:BB:CC:DD:EE:FF'
    >>> MAC(0xAABBCCDDEEFF)
    'AA:BB:CC:DD:EE:FF'
    >>> MAC("AABBCCDDEEFF") + " -- " + MAC("0011.2233.4455")
    'AA:BB:CC:DD:EE:FF -- 00:11:22:33:44:55'
    """

    def __new__(cls, mac: INPUT_TYPES):
        if isinstance(mac, MAC):
            return mac
        return super().__new__(cls, cls._clean(mac))

    def __int__(self) -> int:
        return int(self.replace(":", ""), 16)

    @classmethod
    def _clean(cls, mac: INPUT_TYPES) -> str:
        def qm(value: str) -> str:
            return ":".join(f"{value[i : i + 2]}" for i in range(0, 12, 2))

        match mac:
            case int():
                return ":".join(f"{(mac >> shift) & 0xFF:02X}" for shift in (40, 32, 24, 16, 8, 0))
            case bytes() if len(mac) == 6:
                return ":".join(f"{b:02X}" for b in mac)
            case str() if len(mac) == 6:
                return ":".join(f"{ord(c):02X}" for c in mac)
            case bytes():
                value = mac.decode(encoding="utf-8", errors="strict").upper()
            case str():
                value = mac.upper()
            case _:
                raise ValueError(f"Invalid MAC: {mac}")

        match = rx_mac_address_solid.match(value)
        if match:
            return qm(value)
        match = rx_mac_address_cisco_media.match(value)
        if match:
            return qm(value.replace(".", "")[2:])
        match = rx_mac_address_cisco.match(value)
        if match:
            return qm(value.replace(".", "").replace("-", ""))
        match = rx_mac_address_hp.match(value)
        if match:
            return qm(value.replace("-", ""))
        value = value.replace("-", ":")
        match = rx_mac_address_sixblock.match(value)
        if not match:
            raise ValueError(f"Invalid MAC: {mac}")
        r: list[str] = []
        for i in range(1, 7):
            v = match.group(i)
            if len(v) == 1:
                v = f"0{v}"
            r.append(v)
        return qm("".join(r))

    def to_cisco(self) -> str:
        """
        Convert to Cisco-like format

        >>> MAC("AA:BB:CC:DD:EE:FF").to_cisco()
        'aabb.ccdd.eeff'
        """
        r = self.lower().replace(":", "")
        return f"{r[:4]}.{r[4:8]}.{r[8:]}"

    def shift(self, count: int) -> str:
        """
        Return shifted MAC address

        >>> MAC("AA:BB:CC:DD:EE:FF").shift(0)
        'AA:BB:CC:DD:EE:FF'
        >>> MAC("AA:BB:CC:DD:EE:FF").shift(1)
        'AA:BB:CC:DD:EF:00'
        >>> MAC("AA:BB:CC:DD:EE:FF").shift(256)
        'AA:BB:CC:DD:EF:FF'
        >>> MAC("AA:BB:CC:DD:EE:FF").shift(257)
        'AA:BB:CC:DD:F0:00'
        >>> MAC("AA:BB:CC:DD:EE:FF").shift(4096)
        'AA:BB:CC:DD:FE:FF'

        :return:
        """
        # Convert to 64-bit integer
        v = 0
        for part in self.split(":"):
            v = (v << 8) | int(part, 16)
        # Shift count addresses
        v += count
        # Convert back to MAC
        return ":".join(f"{(v >> shift) & 0xFF:02X}" for shift in (40, 32, 24, 16, 8, 0))

    @property
    def is_multicast(self) -> bool:
        """
        Check if MAC address is multicast one
        :return: True if MAC is multicast
        """
        return bool(int(self.split(":", 1)[0], 16) & 0x1)

    @property
    def is_locally_administered(self) -> bool:
        """
        Locally-Administered-MAC-addresses
        A locally administered address is assigned to a device by a network administrator,
        overriding the burned-in address.
        In this case, the second-least-significant bit of the first octet of the address is a 1.
           * x2-xx-xx-xx-xx-xx
           * x6-xx-xx-xx-xx-xx
           * xA-xx-xx-xx-xx-xx
           * xE-xx-xx-xx-xx-xx
        """
        return bool(int(self.split(":", 1)[0], 16) & 0x2)

    @property
    def is_private(self) -> bool:
        """Check if MAC address on Private Range: F0:3F:03:00:00:00 - F0:3F:03:FF:FF:FF"""
        return self.startswith("F0:3F:03")

    @classmethod
    def distance(cls, s: INPUT_TYPES, e: INPUT_TYPES) -> int:
        """
        Calculate distance between MACs.

        Order is insignificant.

        Args:
            m1: first mac.
            m2: last mac.

        Returns:
            Distance between MACs.
        """
        return abs(int(MAC(s)) - int(MAC(e)))

    @property
    def oui(self) -> int:
        """
        Returns organization unique identifier of MAC.
        """
        return int(self) >> 24

    @classmethod
    def is_same_oui(cls, s: INPUT_TYPES, *args: INPUT_TYPES) -> bool:
        """
        Check if both macs belongs to same vendor's organization unique identifiers.
        """
        if not args:
            return True
        oui = MAC(s).oui
        return all(MAC(a).oui == oui for a in args)
