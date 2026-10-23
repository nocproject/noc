# ----------------------------------------------------------------------
# IP address manipulation routines
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import annotations

import socket
import struct
from collections.abc import Iterable, Callable

# NOC Modules
from noc.core.validators import check_ipv4_prefix, check_ipv6_prefix

# Bit masks
B16 = 0xFFFF
B32 = 0xFFFFFFFF


class IP:
    """Base class for IP prefix.

    Attributes:
        afi: Address family identifier ("4" or "6"). Default is None.
    """

    afi = None

    def __init__(self, prefix: str) -> None:
        """Return new prefix instance.

        Args:
            prefix: String containing prefix in the form address/mask.
        """
        self.prefix = prefix
        self.address, self.mask = prefix.split("/")
        self.mask = int(self.mask)

    def __repr__(self) -> str:
        """Returns string representation of prefix."""
        return f"<IPv{self.afi} {self.prefix}>"

    def __str__(self) -> str:
        """Returns string containing prefix."""
        return self.prefix

    def __len__(self) -> int:
        """Returns mask length (in bits)."""
        return self.mask

    def __cmp__(self, other) -> int:
        """Compare prefix with another.

        Args:
            other: IP instance to be compared.

        Returns:
             0 if the prefixes are equal, negative if this prefix is less than
             *other*, positive if greater.
        """
        if self == other:
            return 0
        if self < other:
            return -1
        return 1

    def __le__(self, other):
        """><= operator."""
        return self == other or self < other

    def __ge__(self, other):
        """>= operator."""
        return self == other or self > other

    def __contains__(self, other):
        """Check if *other* is contained within this prefix.

        Resolves string arguments to IP instances automatically and raises
        when address families don't match.
        """
        if isinstance(other, str):
            other = IP.prefix(other)
        if self.afi != other.afi:
            raise ValueError("Mismatched address families")
        return self.contains(other)

    @classmethod
    def get_afi(cls, prefix) -> str:
        """Return the address family identifier for a prefix string."""
        if ":" in prefix:
            return "6"
        return "4"

    @classmethod
    def prefix(cls, prefix) -> IPv4 | IPv6:
        """Convert a string to the appropriate IP prefix instance.

        Args:
            prefix: String containing an IPv4 or IPv6 prefix.

        Returns:
            IPv4 or IPv6 instance.
        """
        if ":" in prefix:
            return IPv6(prefix)
        return IPv4(prefix)

    def iter_address(
        self,
        count: int | None = None,
        until: str | IP | None = None,
        filter: Callable[[IP], bool] | None = None,
    ):
        """Yield continuing addresses beginning from this prefix.

        Args:
            count: Stop after yielding this many addresses.
            until: Stop when reaching this address (IP instance or string).
            filter: Optional callable that accepts an IP instance and returns
                a boolean; only addresses where it returns True are yielded.

        Yields:
            IP instances starting from *self* and incrementing by one.
        """
        if until and isinstance(until, str):
            until = self.__class__(until)
        if until:
            until += 1
        n = 0
        a = self
        while True:
            if filter is None or filter(a):
                yield a
            a += 1
            n += 1
            if (count and n >= count) or (until and a == until):
                return

    def iter_cover(self, mask: int) -> Iterable[IP]:
        """Generate prefixes of size *mask* covering this prefix.

        Args:
            mask: Target prefix length. Must be >= this prefix's mask.

        Yields:
            IP instances whose combined range covers the original prefix.
        """
        if mask < self.mask:
            return
        if mask == self.mask:
            yield self
            return
        s = IP.prefix(self.prefix.split("/")[0] + f"/{int(mask)}")
        maxmask = 32 if self.afi == "4" else 128
        dist = 2 ** (maxmask - mask)
        for i in range(2 ** (mask - self.mask)):
            yield s
            s += dist

    def iter_free(self, prefixes: list[IP]):
        """Yield free sub-prefixes within this prefix.

        Args:
            prefixes: List of occupied prefixes (strings or IP instances).

        Yields:
            IP instances representing free (unoccupied) sub-prefixes.
        """
        # Fill Tree
        db = PrefixDB()
        n = 0
        for p in prefixes:
            if isinstance(p, str):
                p = self.__class__(p)
            db[p] = True
            n += 1
        if n == 0:
            yield self
            return
        yield from db.iter_free(self)

    def area_spot(
        self,
        addresses: list[str | IP],
        dist: int,
        sep: bool = False,
        exclude_special: bool = True,
    ) -> list[IP | None]:
        """Return addresses inside the prefix covering an area around the given ones.

        Args:
            addresses: List of used addresses (strings or IP instances).
            dist: Distance (in addresses) to include around each used address.
            sep: Insert None into the result list where gaps appear between
                adjacent areas.
            exclude_special: Exclude broadcast and network addresses from the
                result.

        Returns:
            List of IP instances (and optionally None gap markers).
        """
        if not addresses:
            return []
        s_first = self.first.set_mask()
        s_last = self.last.set_mask()
        # Return all addresses except network and broadcast
        # for IPv4, when a dist is larger than network size
        if self.afi == "4" and dist >= self.size:
            if exclude_special:
                ignored = self.special_addresses
                return [a for a in s_first.iter_address(until=s_last) if a not in ignored]
            return list(s_first.iter_address(until=s_last))
        # Left only addresses remaining in prefix and convert them to
        # IP instances
        addresses = {
            a
            for a in [IP.prefix(a) if isinstance(a, str) else a for a in addresses]
            if self.contains(a)
        }
        addresses = sorted(addresses)
        # Fill the spot
        spot = []
        last = None
        last_touched = None
        for a in addresses:
            # Fill spot around the first address
            if last is None:
                last_touched = min(a + dist, s_last)
                spot = list(max(a - dist, s_first).iter_address(until=last_touched))
            else:
                if a <= last + dist:
                    # No gap, fill d addresses from last touched
                    lt = min(last_touched + (a - last), s_last)
                    spot += list((last_touched + 1).iter_address(until=lt))
                else:
                    # Gap, insert separator if needed
                    if sep:
                        spot.append(None)
                    # Fill spot around address
                    lt = min(a + dist, s_last)
                    sf = max(a - dist, last)
                    spot += list(sf.iter_address(until=lt))
                last_touched = lt
            # Exit if last address touched
            if last_touched == s_last:
                break
            last = a
        # Return result
        if exclude_special:
            ignored = self.special_addresses
            if ignored:
                return [a for a in spot if a is None or a not in ignored]
        return spot

    def rebase(self, base: IP, new_base: IP) -> IPv4 | IPv6:
        """Rebase this prefix from *base* to *new_base*.

        Args:
            base: Original base prefix.
            new_base: New base prefix.

        Returns:
            Rebased IP instance (same family as *self*).
        """
        if self == base:
            return new_base
        pb = list(self.iter_bits())[base.mask :]
        nb = list(new_base.iter_bits()) + [0] * (base.mask - new_base.mask) + pb
        return self.from_bits(nb)

    @staticmethod
    def expand(addr: str) -> str:
        """Expand and normalize an address for reliable key lookup.

        Dispatches the address family and delegates to the appropriate subclass
        expand method.

        Args:
            addr: IPv4 or IPv6 address string.

        Returns:
            Expanded/normalized address string.
        """
        if ":" in addr:
            return IPv6.expand(addr)
        return IPv4.expand(addr)

    @property
    def special_addresses(self):
        """Set of 'special' addresses for this prefix (e.g., network or broadcast)."""
        return set()


class IPv4(IP):
    """IPv4 prefix. Internally stored as an unsigned 32-bit integer and mask."""

    afi = "4"

    def __init__(self, prefix: str, netmask: str | None = None) -> None:
        """Create a new IPv4 prefix.

        Args:
            prefix: Address string in format X.X.X.X or X.X.X.X/Y.
            netmask: Optional netmask in X.X.X.X format (used when *prefix*
                has no /Y suffix).
        """
        if "/" not in prefix:
            if netmask:
                prefix += f"/{int(self.netmask_to_len(netmask))}"
            else:
                prefix += "/32"
        check_ipv4_prefix(prefix)
        super().__init__(prefix)
        # Convert to int
        self.d = struct.unpack("!I", socket.inet_aton(self.address))[0]

    @classmethod
    def netmask_to_len(cls, netmask: str) -> int:
        """Return the CIDR mask length for a dotted-decimal netmask string."""
        n = 0
        for m in [int(d) for d in netmask.split(".")]:
            if m == 255:
                n += 8
            else:
                x = 128
                while x:
                    if m & x:
                        n += 1
                        x >>= 1
                    else:
                        break
                break
        return n

    def _get_parts(self) -> list[int]:
        """Get a list of the 4 IPv4 octets (as integers).

        Returns:
            List of 4 integers.
        """
        return [int(d) for d in self.address.split(".")]

    @classmethod
    def _to_prefix(cls, s: int, mask: int) -> IPv4:
        """Convert an integer and mask length into a new IPv4 instance.

        Args:
            s: Integer representation of the address (unsigned 32-bit).
            mask: Mask length (0..32).

        Returns:
            New IPv4 instance.
        """
        return IPv4(
            f"{int(s >> 24 & 255)}.{int(s >> 16 & 255)}.{int(s >> 8 & 255)}.{int(s & 255)}/{int(mask)}"
        )

    def __hash__(self) -> int:
        """Hash the IPv4 instance."""
        return self.d

    def __eq__(self, other):
        """== operator."""
        return self.afi == other.afi and self.d == other.d and self.mask == other.mask

    def __ne__(self, other):
        """!= operator."""
        return self.afi != other.afi or self.d != other.d or self.mask != other.mask

    def __lt__(self, other):
        """< operator."""
        return self.d < other.d or (self.d == other.d and self.mask < other.mask)

    def __gt__(self, other):
        """> operator."""
        return self.d > other.d or (self.d == other.d and self.mask > other.mask)

    def __add__(self, n: int) -> IPv4:
        """Add an integer distance to this address.

        Args:
            n: Distance to add.

        Returns:
            New IPv4 instance.
        """
        return self._to_prefix((self.d + n) & B32, self.mask)

    def __sub__(self, n: int | IPv4) -> IPv4 | int:
        """Subtract an integer or compute distance to another IPv4 address.

        If *n* is an integer, returns a new IPv4 instance shifted by *n*.
        If *n* is an IPv4 instance, returns the numeric distance between addresses.

        Args:
            n: Integer distance or IPv4 instance.

        Returns:
            New IPv4 instance (when *n* is int) or integer distance (when *n* is IPv4).
        """
        if isinstance(n, IPv4):
            return self.d - n.d
        d = self.d - n
        if d < 0:
            d = B32 + self.d
        return self._to_prefix(d, self.mask)

    def iter_bits(self):
        """Yield up to *mask* bits of this prefix.

        Yields:
            0 or 1 for each bit position from most significant down.
        """
        m = 1 << 31
        for i in range(self.mask):
            yield 1 if self.d & m else 0
            m >>= 1

    @classmethod
    def from_bits(cls, bits: list[int]) -> IPv4:
        """Create a new IPv4 instance from a list of bits.

        Args:
            bits: List of 0 or 1 values.

        Returns:
            New IPv4 instance whose mask length equals the number of bits.
        """
        d = 0
        n = 0
        for b in bits:
            d = (d << 1) | b
            n += 1
        if n < 32:
            d <<= 32 - n
        return cls._to_prefix(d, n)

    @property
    def size(self) -> int:
        """Get the number of addresses in this prefix."""
        return 2 ** (32 - self.mask)

    @property
    def first(self) -> IPv4:
        """Return the first address of the block (network address)."""
        return self._to_prefix(self.d & (((1 << self.mask) - 1) << (32 - self.mask)), self.mask)

    @property
    def last(self) -> IPv4:
        """Return the last address of the block (broadcast address)."""
        return self._to_prefix(
            self.d | (B32 ^ (((1 << self.mask) - 1) << (32 - self.mask))), self.mask
        )

    @property
    def netmask(self) -> IPv4:
        """Return an IPv4 instance representing the netmask in dotted-decimal form."""
        return self._to_prefix(((1 << self.mask) - 1) << (32 - self.mask), 32)

    @property
    def wildcard(self) -> IPv4:
        """Return an IPv4 instance representing the Cisco-style wildcard mask."""
        return self._to_prefix((2 ** (32 - self.mask)) - 1, 32)

    def contains(self, other: IPv4) -> bool:
        """Check if *other* is contained within this prefix.

        Args:
            other: Another IPv4 instance.

        Returns:
            True if *other* falls inside this prefix.
        """
        if self.mask > other.mask:
            return False
        m = ((1 << self.mask) - 1) << (32 - self.mask)
        return (self.d & m) == (other.d & m)

    @property
    def normalized(self) -> IPv4:
        """Return a new IPv4 instance in normalized minimal form."""
        return self._to_prefix(self.d & ((1 << self.mask) - 1) << (32 - self.mask), self.mask)

    def set_mask(self, mask: int = 32) -> IPv4:
        """Return a new IPv4 instance with the specified mask value.

        Args:
            mask: New mask length (default 32).

        Returns:
            New IPv4 instance with the same address and new mask.
        """
        return self._to_prefix(self.d, mask)

    @classmethod
    def range_to_prefixes(
        cls,
        first: str | IPv4,
        last: str | IPv4,
    ) -> list[IPv4]:
        """Convert an IPv4 address range to a minimal list of covering prefixes.

        >>> IPv4.range_to_prefixes('192.168.0.2', '192.168.0.2')
        [<IPv4 192.168.0.2/32>]
        >>> IPv4.range_to_prefixes('192.168.0.2', '192.168.0.16')
        [<IPv4 192.168.0.2/31>, <IPv4 192.168.0.4/30>, <IPv4 192.168.0.8/29>, <IPv4 192.168.0.16/32>]
        >>> IPv4.range_to_prefixes('0.0.0.0', '255.255.255.255')
        [<IPv4 0.0.0.0/0>]

        Args:
            first: First address in the range (string or IPv4 instance).
            last: Last address in the range (string or IPv4 instance).

        Returns:
            Minimal list of IPv4 prefixes that exactly cover the range.
        """
        r = []
        if isinstance(first, str):
            first = IPv4(first)
        if isinstance(last, str):
            last = IPv4(last)
        while first <= last:
            d = first.d
            n = 0
            m = 2
            while d % m == 0 and n < 32:
                if IPv4(f"{first.prefix.split('/')[0]}/{int(31 - n)}").last < last:
                    n += 1
                    m <<= 1
                else:
                    break
            pfx = IPv4(f"{first.prefix.split('/')[0]}/{int(32 - n)}")
            r.append(pfx)
            nfirst = pfx.last + 1
            if nfirst.d == first.d:
                # 255.255.255.255 + 1 -> 0.0.0.0
                break
            first = nfirst
        return r

    @staticmethod
    def expand(addr: str) -> str:
        """IPv6.expand compatibility stub — returns the address unchanged."""
        return addr

    @property
    def special_addresses(self) -> set[IPv4]:
        """Set of 'special' addresses for this IPv4 prefix.

        Returns the first and last addresses (network and broadcast) when
        the mask is less than /31; otherwise returns the parent result.
        """
        sa = super().special_addresses
        if self.mask < 31:
            sa.add(self.first.set_mask())
            sa.add(self.last.set_mask())
        return sa

    @property
    def is_loopback(self) -> bool:
        """Check if this address is in the loopback range (127.0.0.0/8)."""
        return self in LOOPBACK_IPv4

    @property
    def is_private(self) -> bool:
        """Check if this address is in a private range.

        Covers 10.0.0.0/8, 100.64.0.0/10, 172.16.0.0/12,
        192.0.0.0/24, 192.168.0.0/16.
        """
        return self in private_ips

    @property
    def is_link_local(self) -> bool:
        """Check if this address is link-local (169.254.0.0/16)."""
        return self in LINK_LOCAL_IPv4


class IPv6(IP):
    """IPv6 prefix. Internally stored as four 32-bit integers."""

    afi = "6"

    def __init__(self, prefix: str, netmask: str | None = None) -> None:
        """Create a new IPv6 prefix instance.

        Args:
            prefix: Address string in compressed or expanded form with optional mask.
            netmask: Optional netmask in full IPv6 notation (used when *prefix*
                has no /Y suffix).
        """
        if "/" not in prefix:
            if netmask:
                prefix += f"/{IPv6.mask_to_bits(netmask)}"
            else:
                prefix += "/128"
        check_ipv6_prefix(prefix)
        super().__init__(prefix)
        # Convert to 4 ints
        p = self._get_parts()
        self.d0 = (p[0] << 16) + p[1]
        self.d1 = (p[2] << 16) + p[3]
        self.d2 = (p[4] << 16) + p[5]
        self.d3 = (p[6] << 16) + p[7]

    @staticmethod
    def __split_parts(address: str) -> list[int]:
        """Parse an IPv6 address string into a list of 8 integers.

        Handles :: compression, dotted-decimal suffixes, and leading zeros.

        Args:
            address: IPv6 address in compressed form.

        Returns:
            List of 8 integers (16-bit each).
        """
        if address == "::":
            return [0, 0, 0, 0, 0, 0, 0, 0]
        parts = address.split(":")
        if "." in parts[-1]:
            p = [int(x) for x in parts[-1].split(".")]
            parts = [*parts[:-1], f"{p[0]:02x}{p[1]:02x}", f"{p[2]:02x}{p[3]:02x}"]
        if len(parts) == 8:
            parts = [pp if pp else "0" for pp in parts]
        else:
            # Expand ::
            i = parts.index("")
            h = []
            if i > 0:
                h = parts[:i]
            if i + 1 < len(parts) and not parts[i + 1]:
                i += 1
            t = parts[i + 1 :]
            parts = h + ["0"] * (8 - len(h) - len(t)) + t
        return [int(pp, 16) for pp in parts]

    @staticmethod
    def mask_to_bits(mask: str) -> int:
        """Count the number of set bits in an IPv6 mask string."""
        n = 0
        for p in IPv6.__split_parts(mask):
            n += bin(p).count("1")
        return n

    def _get_parts(self) -> list[int]:
        """Parse this prefix's address into a list of 8 integers.

        Returns:
            List of 8 integers (16-bit each).
        """
        return IPv6.__split_parts(self.address)

    def _get_masks(self) -> list[int]:
        """Return four 32-bit integers representing the bit mask.

        Returns:
            List of 4 integers forming the network mask.
        """
        masks = []
        mask = self.mask
        while mask:
            if mask >= 32:
                masks.append(0xFFFFFFFF)
                mask -= 32
            else:
                masks.append(((1 << mask) - 1) << (32 - mask))
                mask = 0
        masks += [0] * (4 - len(masks))
        return masks

    @classmethod
    def _to_prefix(cls, d0: int, d1: int, d2: int, d3: int, mask: int) -> IPv6:
        """Convert four 32-bit integers and a mask into a new IPv6 instance.

        Applies :: compression where appropriate and expands mapped IPv4
        addresses (::ffff:x.x.x.x) back to mixed notation.

        Args:
            d0-d3: Four 32-bit integers forming the address.
            mask: Mask length (0..128).

        Returns:
            New IPv6 instance.
        """
        r = [
            (d0 >> 16) & B16,
            d0 & B16,
            (d1 >> 16) & B16,
            d1 & B16,
            (d2 >> 16) & B16,
            d2 & B16,
            (d3 >> 16) & B16,
            d3 & B16,
        ]
        # Format groups
        if r[:-3] == [0, 0, 0, 0, 0] and r[-3] == 0xFFFF:
            return IPv6(
                f"::ffff:{int(r[-2] >> 8)}.{int(r[-2] & 255)}.{int(r[-1] >> 8)}.{int(r[-1] & 255)}/{int(mask)}"
            )
        # Compact longest zeroes sequence
        lp = 0
        ll = 0
        cp = 0
        while True:
            try:
                i = r.index(0, cp)
            except ValueError:
                break
            s = i
            ln = 1
            while s + ln < len(r) and r[s + ln] == 0:
                ln += 1
            if ln > ll:
                lp = s
                ll = ln
            cp = s + ln
        if ll:
            h = r[:lp]
            t = r[lp + ll :]
            return IPv6(
                f"{':'.join([f'{p:x}' for p in h])}::{':'.join([f'{p:x}' for p in t])}/{int(mask)}"
            )
        return IPv6(":".join([f"{p:x}" for p in r]) + f"/{int(mask)}")

    def __hash__(self) -> int:
        """Hash the IPv6 instance (by prefix string)."""
        return hash(self.prefix)

    def __eq__(self, other):
        """== operator."""
        return (
            self.afi == other.afi
            and self.d0 == other.d0
            and self.d1 == other.d1
            and self.d2 == other.d2
            and self.d3 == other.d3
            and self.mask == other.mask
        )

    def __ne__(self, other):
        """!= operator."""
        return (
            self.d0 != other.d0
            or self.d1 != other.d1
            or self.d2 != other.d2
            or self.d3 != other.d3
            or self.mask != other.mask
        )

    def __lt__(self, other):
        """< operator. Compare numeric value first, then mask."""
        if self.d0 != other.d0:
            return self.d0 < other.d0
        if self.d1 != other.d1:
            return self.d1 < other.d1
        if self.d2 != other.d2:
            return self.d2 < other.d2
        if self.d3 == other.d3:
            return self.mask < other.mask
        return self.d3 < other.d3

    def __gt__(self, other):
        """> operator. Compare numeric value first, then mask."""
        if self.d0 != other.d0:
            return self.d0 > other.d0
        if self.d1 != other.d1:
            return self.d1 > other.d1
        if self.d2 != other.d2:
            return self.d2 > other.d2
        if self.d3 == other.d3:
            return self.mask > other.mask
        return self.d3 > other.d3

    def __add__(self, n: int) -> IPv6:
        """Add an integer distance to this address.

        Args:
            n: Integer distance to add.

        Returns:
            New IPv6 instance.
        """
        d3 = self.d3 + n
        d2 = self.d2
        d1 = self.d1
        d0 = self.d0
        if d3 > B32:
            d3 &= B32
            d2 += 1
        if d2 > B32:
            d2 &= B32
            d1 += 1
        if d1 > B32:
            d1 &= B32
            d0 += 1
        if d0 > B32:
            d0 &= B32
            # d3+=1
        return self._to_prefix(d0, d1, d2, d3, self.mask)

    def __sub__(self, n) -> IPv6 | int:
        """Subtract an integer or compute distance to another IPv6 prefix.

        If *n* is an integer, returns a new IPv6 instance shifted by *n*.
        If *n* is an IPv6 instance, returns the approximate distance between the two
        prefixes (32-bit arithmetic on the least significant word).

        Args:
            n: Integer distance or IPv6 instance.

        Returns:
            New IPv6 instance (when *n* is int) or integer distance (when *n* is IPv6).
        """
        d3 = self.d3
        d2 = self.d2
        d1 = self.d1
        d0 = self.d0
        if isinstance(n, IPv6):
            # Rough 32-bit arithmetic
            return self.d3 - n.d3
        d3 -= n
        if d3 < 0:
            d3 = B32 + d3 + 1
            d2 -= 1
        if d2 < 0:
            d2 = B32 + d2 + 1
            d1 -= 1
        if d1 < 0:
            d1 = B32 + d1 + 1
            d0 -= 1
        if d0 < 0:
            d0 = B32 + d0 + 1
            d3 -= 1
        return self._to_prefix(d0, d1, d2, d3, self.mask)

    def iter_bits(self):
        """Yield *mask* bits of this prefix (most significant first).

        Yields:
            0 or 1 for each bit position.
        """
        d = [self.d0, self.d1, self.d2, self.d3]
        for i in range(self.mask):
            if i % 32 == 0:
                cd = d.pop(0)
                m = 1 << 31
            yield 1 if cd & m else 0
            m >>= 1

    @classmethod
    def from_bits(cls, bits: list[int]) -> IPv6:
        """Create a new IPv6 prefix instance from a list of bits.

        Args:
            bits: List of 0 or 1 values.

        Returns:
            New IPv6 instance whose mask length equals the number of bits.
        """
        d = [0, 0, 0, 0]
        n = 0
        for b in bits:
            d[n // 32] = (d[n // 32] << 1) | b
            n += 1
        if n % 32:
            d[n // 32] <<= 32 - (n % 32)
        return cls._to_prefix(d[0], d[1], d[2], d[3], n)

    def contains(self, other: IPv6) -> bool:
        """Check if *other* is contained within this prefix.

        Args:
            other: Another IPv6 instance.

        Returns:
            True if *other* falls inside this prefix.
        """
        if self.mask > other.mask:
            return False
        for a1, a2, m in zip(
            [self.d0, self.d1, self.d2, self.d3],
            [other.d0, other.d1, other.d2, other.d3],
            self._get_masks(),
        ):
            if not m:
                return True
            if (a1 & m) != (a2 & m):
                return False
        return True

    @property
    def first(self) -> IPv6:
        """Return the first address of this prefix (network address)."""
        masks = self._get_masks()
        return self._to_prefix(
            self.d0 & masks[0],
            self.d1 & masks[1],
            self.d2 & masks[2],
            self.d3 & masks[3],
            self.mask,
        )

    @property
    def last(self) -> IPv6:
        """Return the last address of this prefix (broadcast address)."""
        masks = [B32 ^ m for m in self._get_masks()]
        return self._to_prefix(
            self.d0 | masks[0],
            self.d1 | masks[1],
            self.d2 | masks[2],
            self.d3 | masks[3],
            self.mask,
        )

    @property
    def normalized(self) -> IPv6:
        """Return a new IPv6 instance in its normalized minimal form."""
        return self._to_prefix(self.d0, self.d1, self.d2, self.d3, self.mask)

    def set_mask(self, mask: int = 128) -> IPv6:
        """Return a new IPv6 instance with the specified mask value.

        Args:
            mask: New mask length (default 128).

        Returns:
            New IPv6 instance with the same address and new mask.
        """
        return self._to_prefix(self.d0, self.d1, self.d2, self.d3, mask)

    @property
    def digits(self) -> list[str]:
        """Return the 32 hexadecimal digits of this address as a list."""
        return list(
            "".join([f"{self.d0:08x}", f"{self.d1:08x}", f"{self.d2:08x}", f"{self.d3:08x}"])
        )

    def ptr(self, origin_len: int) -> str:
        """Return the PTR value for IPv6 reverse DNS lookup.

        Args:
            origin_len: Number of trailing nibbles to omit (origin length).

        Returns:
            Dot-separated hex string suitable for _ip6 suffix.
        """
        r = self.digits[origin_len:]
        r.reverse()
        return ".".join(r)

    @staticmethod
    def expand(addr: str) -> str:
        """Expand the :: compression in an IPv6 address.

        Replaces :: with the appropriate number of :0: groups.

        Args:
            addr: Compressed IPv6 address string.

        Returns:
            Expanded address (no :: shorthand).
        """
        ni = addr.find("::")
        if ni < 0:
            return addr
        lp = addr.count(":", 0, ni)
        if ni > 0:
            lp += 1
        rp = addr.count(":", ni + 2)
        if ni + 2 < len(addr):
            rp += 1
        np = lp + rp
        xs = ":".join(["0"] * (8 - np))
        if lp:
            xs = f":{xs}"
        if rp:
            xs = f"{xs}:"
        return addr.replace("::", xs)


class PrefixDB:
    """Generalized binary-tree prefix lookup database.

    Stores keys indexed by the bit-path of an IPv4 or IPv6 prefix for efficient
    containment lookups and free-space iteration.

    Attributes:
        children: Tuple of two child nodes (bit=0, bit=1).
        key: Value stored at this node (None if empty).
    """

    def __init__(self, key=None) -> None:
        self.children = [None, None]
        self.key = key

    def __getitem__(self, prefix: IPv4 | IPv6):
        """Get the value stored for *prefix*.

        Args:
            prefix: IPv4 or IPv6 instance to look up.

        Returns:
            The key stored at that node.

        Raises:
            KeyError: When no key is stored for the given prefix.
        """
        node = self
        for n in prefix.iter_bits():
            c = node.children[n]
            if c is None:
                break
            node = c
        if node.key:
            return node.key
        raise KeyError

    def __setitem__(self, prefix: IPv4 | IPv6, key):
        """Store a *key* at the location identified by *prefix*.

        Creates intermediate nodes automatically.

        Args:
            prefix: IPv4 or IPv6 instance as the lookup path.
            key: Value to store at this node.
        """
        node = self
        for n in prefix.iter_bits():
            c = node.children[n]
            if c is None:
                c = self.__class__(node.key)
                node.children[n] = c
            node = c
        node.key = key

    def __contains__(self, prefix: IPv4 | str) -> bool:
        """Check whether a key is stored for *prefix*."""
        if isinstance(prefix, str):
            prefix = IPv4.prefix(prefix)
        node = self
        for n in prefix.iter_bits():
            c = node.children[n]
            if c is None:
                break
            node = c
        return bool(node.key)

    def iter_free(self, root: IPv4 | IPv6):
        """Yield free (unoccupied) sub-prefixes within *root*.

        Walks the tree starting at the bit-path of *root* and yields every
        prefix whose node has no stored key.

        Args:
            root: IPv4 or IPv6 prefix that bounds the search.

        Yields:
            IP instances (same family as *root*) representing free sub-prefixes.
        """

        def walk_tree(c, root_bits):
            for n, v in enumerate(c.children):
                bits = [*root_bits, n]
                if v is None:
                    yield bits
                elif len(bits) < max_bits:
                    nc = c.children[n]
                    if nc.key is None:
                        yield from walk_tree(nc, bits)

        root_bits = list(root.iter_bits())
        afi = root.afi
        max_bits = 32 if afi == "4" else 128
        c = self
        for n in root_bits:
            c = c.children[n]
        # walk tree
        for bits in walk_tree(c, root_bits):
            yield root.__class__.from_bits(bits)

    @classmethod
    def from_prefixes(cls, prefixes: list[IPv4], key) -> "PrefixDB":
        """Create a PrefixDB populated with the same key for all given prefixes.

        Args:
            prefixes: List of IPv4 (or IPv6) instances.
            key: Value to store under each prefix.

        Returns:
            New PrefixDB instance.
        """
        pdb = PrefixDB()
        for p in prefixes:
            pdb[p] = key
        return pdb


LOOPBACK_IPv4 = IP.prefix("127.0.0.0/8")
LINK_LOCAL_IPv4 = IP.prefix("169.254.0.0/16")
PRIVATE_IPv4 = [
    IP.prefix("10.0.0.0/8"),
    IP.prefix("100.64.0.0/10"),
    IP.prefix("172.16.0.0/12"),
    IP.prefix("192.168.0.0/16"),
]
private_ips = PrefixDB.from_prefixes(PRIVATE_IPv4, True)
