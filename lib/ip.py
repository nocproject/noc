# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IP address manipulation routines
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import struct,socket,math
##
##
##
def address_to_int(ip):
    """
    >>> address_to_int("192.168.0.1")
    3232235521
    >>> address_to_int("10.0.0.0")
    167772160
    """
    return struct.unpack("!L",socket.inet_aton(ip))[0]
##
##
##
def int_to_address(i):
    """
    >>> int_to_address(3232235521L)
    '192.168.0.1'
    >>> int_to_address(167772160)
    '10.0.0.0'
    """
    return socket.inet_ntoa(struct.pack("!L",i))
##
## Converts bits to an integer
##
def bits_to_int(bits):
    """
    >>> int_to_address(bits_to_int(24))
    '255.255.255.0'
    >>> int_to_address(bits_to_int(16))
    '255.255.0.0'
    """
    return ((1L<<bits)-1L)<<(32L-bits)
##
## Converts bits to netmask
##
def bits_to_netmask(bits):
    """
    >>> bits_to_netmask(24)
    '255.255.255.0'
    >>> bits_to_netmask(16)
    '255.255.0.0'
    """
    try:
        bits=int(bits)
        if bits<=0 or bits>32:
            raise Exception
    except:
        return "255.255.255.255"
    return int_to_address(bits_to_int(bits))

##
## Returns amount of addresses into prefix of "bits" length
##
def bits_to_size(bits):
    return 1L<<(32L-bits)
##
##
##
def prefix_to_size(prefix):
    n,m=prefix.split("/")
    return bits_to_size(int(m))
##
##
##
def network(prefix):
    n,m=prefix.split("/")
    m=int(m)
    return int_to_address(address_to_int(n)&bits_to_int(m))
##
## Convert arbitrary ip/bits pair to strict network/bits
##
def normalize_prefix(prefix):
    n,m=prefix.split("/")
    m=int(m)
    return "%s/%d"%(int_to_address(address_to_int(n)&bits_to_int(m)),m)
##
## Check wrether address is in prefix
##
def contains(prefix,address):
    """
    >>> contains("10.0.0.0/8","192.168.0.1")
    False
    >>> contains("10.0.0.0/8","10.10.12.5")
    True
    >>> contains("10.0.0.0/16","10.10.12.5")
    False
    """
    n,m=prefix.split("/")
    return network(prefix)==network(address+"/%d"%int(m))
##
##
##
def broadcast(prefix):
    n,m=prefix.split("/")
    m=int(m)
    return int_to_address(address_to_int(n)|(0xFFFFFFFFL^bits_to_int(m)))
##
##
##
def wildcard(prefix):
    n,m=prefix.split("/")
    m=int(m)
    return int_to_address(0xFFFFFFFFL^bits_to_int(m))

##
##
##
def prefix_to_bin(prefix):
    """ 
    Convert prefix to a list of bits
    >>> prefix_to_bin("4.0.0.0/8")
    [0, 0, 0, 0, 0, 1, 0, 0]
    >>> prefix_to_bin("192.168.254.19/32")
    [1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1]
    """
    ip,l=prefix.split("/")
    l=int(l)
    i=address_to_int(ip)
    r=[]
    i=i>>(32-l)
    for j in range(l):
        r=[int(i&1)]+r
        i>>=1
    return r
##
##
##
def bin_to_prefix(s):
    """
    Convert list of bits to prefix
    >>> bin_to_prefix([0, 0, 0, 0, 0, 1, 0, 0])
    '4.0.0.0/8'
    >>> bin_to_prefix([1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1])
    '192.168.254.19/32'
    """
    r=0L
    for c in s:
        r=(r<<1)|c
    l=len(s)
    r<<=(32-l)
    return "%s/%d"%(int_to_address(r),l)
##
## Return prefix boundary - pair of ints
## representing beginnng and the end of the prefix
##
def prefix_boundary(p):
    """
    >>> prefix_boundary("10.0.0.0/8")
    (167772160L, 184549375L)
    >>> prefix_boundary("10.0.0.0/32")
    (167772160L, 167772160L)
    >>> prefix_boundary("0.0.0.0/0")
    (0L, 4294967295L)
    """
    n,m=p.split("/")
    m=int(m)
    a=address_to_int(n)
    b=bits_to_int(m)
    return (a&b,a|(0xFFFFFFFFL^b))
##
## Returns a longest netmask length possible,
## when address still remains network address
## a is an integer
##
def max_mask(a):
    """
    >>> max_mask(0)
    0
    >>> max_mask(address_to_int("255.255.255.255"))
    32
    >>> max_mask(address_to_int("1.1.1.0"))
    24
    >>> max_mask(address_to_int("1.1.0.0"))
    16
    >>> max_mask(address_to_int("1.1.1.128"))
    25
    >>> max_mask(address_to_int("1.1.1.252"))
    30
    """
    if not a:
        return 0
    r=32
    while a and (a&1==0):
        r-=1
        a>>=1
    return r
##
## Generator returning a minimal
## set of prefixes covering the
## ip address range, given by ints
##
def cover_blocks(f,t):
    """
    >>> list(cover_blocks(address_to_int("192.168.0.0"),address_to_int("192.168.0.0")))
    ['192.168.0.0/32']
    >>> list(cover_blocks(address_to_int("192.168.0.0"),address_to_int("192.168.0.255")))
    ['192.168.0.0/24']
    >>> list(cover_blocks(address_to_int("192.168.0.0"),address_to_int("192.168.0.127")))
    ['192.168.0.0/25']
    >>> list(cover_blocks(address_to_int("0.0.0.0"),address_to_int("255.255.255.255")))
    ['0.0.0.0/0']
    >>> list(cover_blocks(address_to_int("192.168.0.5"),address_to_int("192.168.0.14")))
    ['192.168.0.5/32', '192.168.0.6/31', '192.168.0.8/30', '192.168.0.12/31', '192.168.0.14/32']
    """
    while f<=t:
        m=max(max_mask(f),32-int(math.log(t-f+1,2)))
        yield int_to_address(f)+"/%d"%m
        f+=1<<(32-m)
##
## Returns a list of free block in "prefix"
## Allocated should be sorted list
##
def free_blocks(prefix,allocated):
    """
    >>> list(free_blocks("10.0.0.0/8",[]))
    ['10.0.0.0/8']
    >>> list(free_blocks("10.0.0.0/8",["10.0.0.0/8"]))
    []
    >>> list(free_blocks("192.168.0.0/20",["192.168.0.0/24"]))
    ['192.168.1.0/24', '192.168.2.0/23', '192.168.4.0/22', '192.168.8.0/21']
    >>> list(free_blocks("192.168.0.0/20",["192.168.15.0/24"]))
    ['192.168.0.0/21', '192.168.8.0/22', '192.168.12.0/23', '192.168.14.0/24']
    >>> list(free_blocks("192.168.0.0/20",["192.168.8.0/24"]))
    ['192.168.0.0/21', '192.168.9.0/24', '192.168.10.0/23', '192.168.12.0/22']
    >>> list(free_blocks("192.168.0.0/20",["192.168.6.0/23"]))
    ['192.168.0.0/22', '192.168.4.0/23', '192.168.8.0/21']
    >>> list(free_blocks("192.168.0.0/20",["192.168.6.0/24","192.168.7.0/24"]))
    ['192.168.0.0/22', '192.168.4.0/23', '192.168.8.0/21']
    >>> list(free_blocks("192.168.0.0/20",["192.168.0.0/24","192.168.6.0/24","192.168.7.0/24","192.168.15.0/24"]))
    ['192.168.1.0/24', '192.168.2.0/23', '192.168.4.0/23', '192.168.8.0/22', '192.168.12.0/23', '192.168.14.0/24']
    >>> list(free_blocks("192.168.0.0/22",["192.168.0.0/24","192.168.1.0/24","192.168.2.0/24","192.168.3.0/24"]))
    []
    """
    p0,p1=prefix_boundary(prefix)
    f0=p0
    for a in allocated:
        a0,a1=prefix_boundary(a)
        if a0>f0:
            # Free space found
            # Return prefixes covering free space
            for b in cover_blocks(f0,a0-1):
                yield b
        f0=a1+1
    if f0<p1:
        # Free space at the end found
        for b in cover_blocks(f0,p1):
            yield b
##
## Returns minimal prefix containing both IP addresses
##
def minimal_prefix(ip1,ip2):
    """
    >>> minimal_prefix("192.168.0.1","192.168.0.2")
    '192.168.0.0/30'
    >>> minimal_prefix("192.168.0.1","192.168.0.3")
    '192.168.0.0/30'
    >>> minimal_prefix("192.168.0.1","192.168.0.4")
    '192.168.0.0/29'
    >>> minimal_prefix("192.168.0.1","192.168.0.8")
    '192.168.0.0/28'
    >>> minimal_prefix("192.168.0.1","192.168.0.127")
    '192.168.0.0/25'
    >>> minimal_prefix("192.168.0.1","192.168.0.255")
    '192.168.0.0/24'
    >>> minimal_prefix("192.168.0.1","10.0.0.15")
    '0.0.0.0/0'
    >>> minimal_prefix("10.1.12.7","10.0.0.15")
    '10.0.0.0/15'
    """
    for b in range(32,-1,-1):
        suffix="/%d"%b
        n1=network(ip1+suffix)+suffix
        if n1==network(ip2+suffix)+suffix:
            return n1
##
## Compare ip1 against ip2
##
def cmp_ip(ip1,ip2):
    return cmp(address_to_int(ip1),address_to_int(ip2))
##
## Check ip is between f and t
def in_range(ip,f,t):
    return cmp_ip(f,ip)<=0 and cmp_ip(t,ip)>=0
##
##
## Generator returing ip addresses in range
##
def generate_ips(ip1,ip2):
    n1=address_to_int(ip1)
    n2=address_to_int(ip2)
    while True:
        yield int_to_address(n1)
        n1+=1
        if n1>n2:
            break
##
## IPv4 Prefix Database
## 
class PrefixDB(object):
    """
    >>> db=PrefixDB()
    >>> db.append_prefix("192.168.0.0/8","key0")
    >>> db.append_prefix("192.168.1.0/24","key1")
    >>> db.append_prefix("192.168.2.0/24","key2")
    >>> db["10.0.0.0"]
    Traceback (most recent call last):
    ...
    KeyError
    >>> db["192.168.1.1"]
    'key1'
    >>> db["192.168.2.1"]
    'key2'
    >>> db["192.168.3.1"]
    'key0'
    """
    def __init__(self,key=None):
        self.key=key
        self.children=[None,None]
    ## Search for prefix
    def __getitem__(self,key):
        v=self.search(key)
        if v is None:
            raise KeyError
        return v
    ## Generator returning bits of IP address
    @classmethod
    def gen_prefix(cls,prefix):
        ip,l=prefix.split("/")
        l=int(l)
        i=address_to_int(ip)
        m=1L<<31
        for n in range(31,31-l,-1):
            yield (i&m)>>n
            m>>=1
    ## Append prefix to database
    def append_prefix(self,prefix,key):
        node=self
        for n in self.gen_prefix(prefix):
            c=node.children[n]
            if c is None:
                c=self.__class__(node.key)
                node.children[n]=c
            node=c
        node.key=key
    ## Search DB for prefix
    ## And return assotiated key.
    ## Return None when no prefix found
    def search(self,prefix):
        if "/" not in prefix:
            prefix+="/32"
        node=self
        for n in self.gen_prefix(prefix):
            c=node.children[n]
            if c is None:
                break
            node=c
        return node.key
    ##
    ## Load database.
    ## data is an generator returning pairs (prefix,key)
    ##
    def load(self,data):
        for prefix,key in data:
            self.append_prefix(prefix,key)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
