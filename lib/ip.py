# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IP address manipulation routines
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
## NOC Modules
from noc.lib.validators import *

#
B16 = 0xffffL
B32 = 0xffffffffL


class IP(object):
    """Base class for IP prefix"""
    afi = None

    def __init__(self, prefix):
        """
        Return new prefix instance.

        :param prefix: String containing prefix
        :type prefix: str
        """
        self.prefix = prefix
        self.address, self.mask = prefix.split("/")
        self.mask = int(self.mask)

    def __repr__(self):
        """Returns string representation of prefix"""
        return "<IPv%s %s>" % (self.afi, self.prefix)

    def __str__(self):
        """Returns string containing prefix"""
        return self.prefix

    def __unicode__(self):
        """Returns unicode containing prefix"""
        return self.prefix

    def __len__(self):
        """Returns mask length (in bits)"""
        return self.mask

    def __cmp__(self, other):
        """Compare prefix with other

        :param other: IP instance to be compared
        :type other: IP
        :rtype: int
        Returns:

        * 0  -- if prefix equals to other
        * <0 -- if prefix less than other
        * >0 -- if prefix greater than other
        """
        if self == other:
            return 0
        if self < other:
            return -1
        return 1

    def __le__(self, other):
        """<= operator"""
        return self == other or self < other

    def __ge__(self, other):
        """>= operator"""
        return self == other or self > other
    
    def __contains__(self, other):
        """
        "other in self"
        """
        if isinstance(other, basestring):
            other = IP.prefix(other)
        if self.afi != other.afi:
            raise ValueError("Mismatched address families")
        return self.contains(other)

    @classmethod
    def prefix(cls, prefix):
        """
        Convert string to prefix instance.

        :param prefix: String containing IPv4/IPv6 prefix
        :type prefix: str
        :return: IPv6 or IPv6 instance
        :rtype: IPv4 or IPv6 instance
        """
        if ":" in prefix:
            return IPv6(prefix)
        else:
            return IPv4(prefix)

    def iter_address(self, count=None, until=None, filter=None):
        """
        Return generator of continuing addresses beginning from
        prefix instance.

        :param count: Stop after yielding count addresses
        :type count: Integer, Optional
        :param until: Stop when reaching until address
        :type until: IP instance, Optional
        :param filter: Filter addresses through filter callable
        :type filter: Callable accepting IP instance and returning boolean,
            Optional.
        :return: Generator of continuing addresses
        :rtype: Generator of IP instances
        """
        if until and isinstance(until, basestring):
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
                raise StopIteration

    def iter_cover(self, mask):
        """
        Generate prefixes of size _mask_ covering basic prefix
        """
        if mask < self.mask:
            raise StopIteration
        if mask == self.mask:
            yield self
            raise StopIteration
        s = IP.prefix(self.prefix.split("/")[0] + "/%d" % mask)
        maxmask = 32 if self.afi == "4" else 128
        dist = long(2 ** (maxmask - mask))
        for i in range(long(2 ** (mask - self.mask))):
            yield s
            s += dist

    def iter_free(self, prefixes):
        """
        Return generator of free prefixes.

        :param prefixes: List of occupied prefixes
        :type prefixes: list
        :return: Generator of free prefixes
        :rtype: Generator of IP instances
        """
        # Fill Tree
        db = PrefixDB()
        n = 0
        for p in prefixes:
            if isinstance(p, basestring):
                p = self.__class__(p)
            db[p] = True
            n += 1
        if n == 0:
            yield self
            raise StopIteration
        #
        for p in db.iter_free(self):
            yield p

    def area_spot(self, addresses, dist, sep=False):
        """
        Returns a list of addresses, laying inside prefix and containing area
        aroung given addresses

        :param addresses: Used addresses
        :type addresses: list
        :param dist: Distance to spot araund used addresses
        :type dist: int
        :param sep: Insert None into the gaps if sep is True
        :type sep: bool
        :return: List containing area spot
        :rtype: list
        """
        if not addresses:
            return []
        s_first = self.first.set_mask()
        s_last = self.last.set_mask()
        # Return all addresses except network and broadcast
        # for IPv4, when a dist is larger than network size
        if self.afi == "4" and dist >= self.size:
            d = 0 if s_first.address in addresses else 1
            if self.mask == 31:
                return list((s_first + d).iter_address(until=s_last))
            else:
                return list((s_first + d).iter_address(until=s_last - 1))
        # Left only addresses remaining in prefix and convert them to
        # IP instances
        addresses = set(
            a for a in [
                IP.prefix(a) if isinstance(a, basestring) else a for a in addresses
            ] if self.contains(a))
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
                        spot += [None]
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
        if self.afi == "4" and self.mask != 31:
            # Remove network and broadcast address
            return [a for a in spot if (
                a is None or
                a.address not in (self.first.address,
                                  self.last.address))]
        else:
            return spot

    ##
    ## Rebase to a new base
    ##
    def rebase(self, base, new_base):
        pb = list(self.iter_bits())[base.mask:]
        nb = list(new_base.iter_bits()) + [0] * (base.mask - new_base.mask) + pb
        return self.from_bits(nb)


class IPv4(IP):
    """
    IPv4 Prefix. Internally stored as unsigned 32-bit integer and mask
    """
    afi = "4"

    def __init__(self, prefix, netmask=None):
        """
        :param prefix: String in format X.X.X.X or X.X.X.X/Y
        :type prefix: str
        :param netmask: Optional netmask in X.X.X.X format
        :type netmask: str
        """
        if "/" not in prefix:
            if netmask:
                prefix += "/%d" % self.netmask_to_len(netmask)
            else:
                prefix += "/32"
        check_ipv4_prefix(prefix)
        super(IPv4, self).__init__(prefix)
        # Convert to int
        self.d = 0L
        m = 24
        for d in self._get_parts():
            self.d += d << m
            m -= 8

    @classmethod
    def netmask_to_len(cls, netmask):
        """
        Returns netmask mask length
        """
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
        
    def _get_parts(self):
        """
        get list of 4 integers (IPv4 octets)

        :return: List of 4 integers
        :rtype: List of 4 integers
        """
        return [int(d) for d in self.address.split(".")]

    @classmethod
    def _to_prefix(cls, s, mask):
        """
        Convert integer and mask into new IPv4 instance

        :param s: integer representation of address (unsigned 32-bit integer)
        :type s: integer
        :param mask: mask length (0 .. 32)
        :type mask: integer
        """
        return IPv4("%d.%d.%d.%d/%d" % ((s >> 24) & 0xff, (s >> 16) & 0xff,
                                       (s >> 8) & 0xff, s & 0xff, mask))

    def __hash__(self):
        """Hashing"""
        return self.d

    def __eq__(self, other):
        """== operator"""
        return self.afi == other.afi and self.d == other.d and self.mask == other.mask

    def __ne__(self, other):
        """!= operator"""
        return self.afi != other.afi or self.d != other.d or self.mask != other.mask

    def __lt__(self, other):
        """< operator"""
        return self.d < other.d or (self.d == other.d and self.mask < other.mask)

    def __gt__(self, other):
        """> operator"""
        return self.d > other.d or (self.d == other.d and self.mask > other.mask)

    def __add__(self, n):
        """
        + operator.

        :param n: distance
        :type n: integer
        :return: IPv4 instance
        :rtype: IPv4 instance
        """
        return self._to_prefix((self.d + n) & B32, self.mask)

    def __sub__(self, n):
        """
        - operator.
        If argument is integer - returns new IPv4 instance
        If IPv4 instance - returns a distance between addresses

        :param n:
        :type n: IPv4 instance or integer
        :return: Distance or new instance
        :rtype: integer of IPv4 instance
        """
        if isinstance(n, IPv4):
            return self.d - n.d
        else:
            d = self.d - n
            if d < 0:
                d = B32 + self.d
            return self._to_prefix(d, self.mask)

    def iter_bits(self):
        """
        Get generator returning up to mask bits of prefix

        :return: Generator of bits
        :rtype: Generator
        """
        m = 1L << 31
        for i in range(self.mask):
            yield 1 if self.d & m else 0
            m >>= 1
    
    ##
    ## Convert list of bits to a new IPv4 instance
    ##
    @classmethod
    def from_bits(cls, bits):
        """
        Create new IPv4 instance from list of bits

        :param bits: List of 0 or 1
        :return: New IPv4 instance
        :rtype: IPv4 instance
        """
        d = 0
        n = 0
        for b in bits:
            d = (d << 1) | b
            n += 1
        if n < 32:
            d <<= (32 - n)
        return cls._to_prefix(d, n)

    @property
    def size(self):
        """
        Get size of prefix (number of addresses to hold)

        :return: Size of prefix
        :rtype: integer
        """
        return 2 ** (32 - self.mask)

    ##
    ## Returns new IPv4 instance with first address of the block (network)
    ##
    @property
    def first(self):
        """
        :return: First address
        :rtype:
        """
        return self._to_prefix(self.d & (((1L << self.mask) - 1L) << (32L - self.mask)), self.mask)
    
    ##
    ## Returns new IPv4 instance with last address of the block (broadcast)
    ##
    @property
    def last(self):
        return self._to_prefix(self.d | (B32 ^ (((1L << self.mask) - 1L) << (32L - self.mask))), self.mask)
    
    ##
    ## Returns new IPv4 instance holding netmask
    ##
    @property
    def netmask(self):
        return self._to_prefix(((1L << self.mask) - 1L) << (32L - self.mask), 32)
    
    ##
    ## Returns new IPv4 instance with Cisco-style wildcard
    ##
    @property
    def wildcard(self):
        return self._to_prefix((2 ** (32 - self.mask)) - 1, 32)
    
    ##
    ## Check if *other* contained in prefix. Returns bool
    ##
    def contains(self, other):
        if self.mask > other.mask:
            return False
        m = ((1L << self.mask) - 1L) << (32L - self.mask)
        return (self.d & m) == (other.d & m)
    
    ##
    ## Returns new IPv4 instance in normalized minimal possible form
    ##
    @property
    def normalized(self):
        return self._to_prefix(self.d & ((1L << self.mask) - 1L) << (32L - self.mask), self.mask)
    
    ##
    ## Returns new IPv4 instance with new mask value.
    ## If mask not set, returns with /32
    ##
    def set_mask(self, mask=32):
        return self._to_prefix(self.d, mask)

    @classmethod
    def range_to_prefixes(cls, first, last):
        """
        Convert IPv4 address range to minimal list of covering prefixes

        >>> IPv4.range_to_prefixes('192.168.0.2', '192.168.0.2')
        [<IPv4 192.168.0.2/32>]
        >>> IPv4.range_to_prefixes('192.168.0.2', '192.168.0.16')
        [<IPv4 192.168.0.2/31>, <IPv4 192.168.0.4/30>, <IPv4 192.168.0.8/29>, <IPv4 192.168.0.16/32>]
        >>> IPv4.range_to_prefixes('0.0.0.0', '255.255.255.255')
        [<IPv4 0.0.0.0/0>]

        :param cls:
        :param first:
        :param last:
        :return:
        """
        r = []
        if isinstance(first, basestring):
            first = IPv4(first)
        if isinstance(last, basestring):
            last = IPv4(last)
        while first <= last:
            d = first.d
            n = 0
            m = 2
            while d % m == 0 and n < 32:
                if IPv4("%s/%d" % (first.prefix.split("/")[0], 31 - n)).last < last:
                    n += 1
                    m <<= 1
                else:
                    break
            pfx = IPv4("%s/%d" % (first.prefix.split("/")[0], 32 - n))
            r += [pfx]
            nfirst = pfx.last + 1
            if nfirst.d == first.d:
                # 255.255.255.255 + 1 -> 0.0.0.0
                break
            else:
                first = nfirst
        return r

##
## IPv6 prefix
## Internally stored as four 32-bit integers
##
class IPv6(IP):
    afi = "6"
    
    def __init__(self, prefix):
        if "/" not in prefix:
            prefix += "/128"
        check_ipv6_prefix(prefix)
        super(IPv6, self).__init__(prefix)
        # Convert to 4 ints
        p = self._get_parts()
        self.d0 = (p[0] << 16) + p[1]
        self.d1 = (p[2] << 16) + p[3]
        self.d2 = (p[4] << 16) + p[5]
        self.d3 = (p[6] << 16) + p[7]
    
    ##
    ## Convert prefix to a list of 8 integers
    ##
    def _get_parts(self):
        if self.address == "::":
            return [0, 0, 0, 0, 0, 0, 0, 0]
        parts = self.address.split(":")
        if "." in parts[-1]:
            p = [int(x) for x in parts[-1].split(".")]
            parts = parts[:-1] + ["%02x%02x" % (p[0], p[1]), "%02x%02x" % (p[2], p[3])]
        if len(parts) == 8:
            parts = [p if p else "0" for p in parts]
        else:
            # Expand ::
            i = parts.index("")
            h = []
            t = []
            if i > 0:
                h = parts[:i]
            if i + 1 < len(parts) and not parts[i + 1]:
                i += 1
            t = parts[i + 1:]
            parts = h + ["0"] * (8 - len(h) - len(t)) + t
        return [int(p, 16) for p in parts]
    
    ##
    ## Return 4 integers, containing bit mask
    ##
    def _get_masks(self):
        masks = []
        mask = self.mask
        while mask:
            if mask >= 32:
                masks += [0xffffffff]
                mask -= 32
            else:
                masks += [((1L << mask) - 1L) << (32L - mask)]
                mask = 0
        masks += [0] * (4 - len(masks))
        return masks
    
    ##
    ## Convert four 32-bit integers and mask to a new IPv6 instance
    ##
    @classmethod
    def _to_prefix(cls, d0, d1, d2, d3, mask):
        r = [(d0 >> 16) & B16, d0 & B16, (d1 >> 16) & B16, d1 & B16,
             (d2 >> 16) & B16, d2 & B16, (d3 >> 16) & B16, d3 & B16]
        # Format groups
        if r[:-3] == [0, 0, 0, 0, 0] and r[-3] == 0xffff:
            return IPv6("::ffff:%d.%d.%d.%d/%d" % (r[-2] >> 8, r[-2] & 0xff,
                                                   r[-1] >> 8, r[-1] & 0xff,
                                                   mask))
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
            l = 1
            while s + l < len(r) and r[s + l] == 0:
                l += 1
            if l > ll:
                lp = s
                ll = l
            cp = s + l
        if ll:
            h = r[:lp]
            t = r[lp + ll:]
            return IPv6("%s::%s/%d" % (":".join(["%x" % p for p in h]),
                                       ":".join(["%x" % p for p in t]), mask))
        else:
            return IPv6(":".join(["%x" % p for p in r]) + "/%d" % mask)
    
    ##
    ## hash(..)
    ##
    def __hash__(self):
        return hash(self.prefix)
    
    ##
    ## == operator
    ## @todo: reorder comparisons
    def __eq__(self, other):
        return (self.afi == other.afi and self.d0 == other.d0
                and self.d1 == other.d1 and self.d2 == other.d2
                and self.d3 == other.d3 and self.mask == other.mask)
    
    ##
    ## != operator
    ##
    def __ne__(self, other):
        return (self.d0 != other.d0 or self.d1 != other.d1
                or self.d2 != other.d2 or self.d3 != other.d3
                or self.mask != other.mask)
    
    ##
    ## < operator
    ##
    def __lt__(self, other):
        if self.d0 != other.d0:
            return self.d0 < other.d0
        if self.d1 != other.d1:
            return self.d1 < other.d1
        if self.d2 != other.d2:
            return self.d2 < other.d2
        if self.d3 == other.d3:
            return self.mask < other.mask
        return self.d3 < other.d3
    
    ##
    ## > operator
    ##
    def __gt__(self, other):
        if self.d0 != other.d0:
            return self.d0 > other.d0
        if self.d1 != other.d1:
            return self.d1 > other.d1
        if self.d2 != other.d2:
            return self.d2 > other.d2
        if self.d3 == other.d3:
            return self.mask > other.mask
        return self.d3 > other.d3
    
    ##
    ## + operator. Second argument is an integer.
    ## Returns new IPv6 instance
    ##
    def __add__(self, n):
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
            #d3+=1
        return self._to_prefix(d0, d1, d2, d3, self.mask)
    
    ##
    ## - operator. Second argument is an integer or IPv6 instance
    ## Return new IPv6 instance, if second argument is integer,
    ## or distance betweed two prefixes
    ##
    def __sub__(self, n):
        d3 = self.d3
        d2 = self.d2
        d1 = self.d1
        d0 = self.d0
        if isinstance(n, IPv6):
            # Rough 32-bit arithmetic
            return self.d3 - n.d3
        else:
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
    
    ##
    ## Generator returning *mask* bits of prefix
    ##
    def iter_bits(self):
        d = [self.d0, self.d1, self.d2, self.d3]
        for i in range(self.mask):
            if i % 32 == 0:
                cd = d.pop(0)
                m = 1 << 31
            yield 1 if cd & m else 0
            m >>= 1
    
    ##
    ## Convert a list of bits to a new IPv6 prefix instance
    ##
    @classmethod
    def from_bits(cls, bits):
        d = [0, 0, 0, 0]
        n = 0
        for b in bits:
            d[n // 32] = (d[n // 32] << 1) | b
            n += 1
        if n % 32:
            d[n // 32] <<= (32 - (n % 32))
        return cls._to_prefix(d[0], d[1], d[2], d[3], n)
    
    ##
    ## Check if *other* contained within prefix. Returns bool
    ##
    def contains(self, other):
        if self.mask > other.mask:
            return False
        for a1, a2, m in zip([self.d0, self.d1, self.d2, self.d3],
                             [other.d0, other.d1, other.d2, other.d3],
                             self._get_masks()):
            if not m:
                return True
            if (a1 & m) != (a2 & m):
                return False
        return True
    
    ##
    ## Returns new IPv6 instance with first address of prefix
    ##
    @property
    def first(self):
        masks = self._get_masks()
        return self._to_prefix(self.d0 & masks[0], self.d1 & masks[1],
                               self.d2 & masks[2], self.d3 & masks[3],
                               self.mask)
    
    ##
    ## Returns new IPv6 instance with last address of prefix
    ##
    @property
    def last(self):
        masks = [B32 ^ m for m in self._get_masks()]
        return self._to_prefix(self.d0 | masks[0], self.d1 | masks[1],
                               self.d2 | masks[2], self.d3 | masks[3],
                               self.mask)
    
    ##
    ## Returns new IPv6 instance in normalized minimal possible form
    ##
    @property
    def normalized(self):
        return self._to_prefix(self.d0, self.d1, self.d2, self.d3, self.mask)
    
    ##
    ## Returns new IPv4 instance with new mask value.
    ## If mask not set, returns with /128
    ##
    def set_mask(self, mask=128):
        return self._to_prefix(self.d0, self.d1, self.d2, self.d3, mask)
    
    #
    # Returns 32 hexadecimal digits
    #
    @property
    def digits(self):
        return list("".join(["%08x" % self.d0, "%08x" % self.d1,
                             "%08x" % self.d2, "%08x" % self.d3]))
    
    #
    # Returns PTR value for IPv6 reverse zone
    #
    def ptr(self, origin_len):
        r = self.digits[origin_len:]
        r.reverse()
        return ".".join(r)
    

##
## Generalized binary-tree prefix lookup database
##
class PrefixDB(object):
    def __init__(self, key=None):
        self.children = [None, None]
        self.key = key
    
    ##
    ## Get key by prefix
    ##
    def __getitem__(self, prefix):
        node = self
        for n in prefix.iter_bits():
            c = node.children[n]
            if c is None:
                break
            node = c
        if node.key:
            return node.key
        else:
            raise KeyError
    
    ##
    ## Put prefix with key
    ##
    def __setitem__(self, prefix, key):
        node = self
        for n in prefix.iter_bits():
            c = node.children[n]
            if c is None:
                c = self.__class__(node.key)
                node.children[n] = c
            node = c
        node.key = key
    
    ##
    ## Generator returning free blocks
    ##
    def iter_free(self, root):
        def walk_tree(c, root_bits):
            for n, v in enumerate(c.children):
                bits = root_bits + [n]
                if v == None:
                    yield bits
                elif len(bits) < max_bits:
                    nc = c.children[n]
                    if nc.key is None:
                        for f in walk_tree(nc, bits):
                            yield f
        root_bits = list(root.iter_bits())
        afi = root.afi
        max_bits = 32 if afi == "4" else 128
        c = self
        for n in root_bits:
            c = c.children[n]
        # walk tree
        for bits in walk_tree(c, root_bits):
            yield root.__class__.from_bits(bits)
    
