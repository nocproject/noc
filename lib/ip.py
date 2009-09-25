# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IP address manipulation routines
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import struct,socket
##
##
##
def address_to_int(ip):
    """
    >>> address_to_int("192.168.0.1")
    3232235521L
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
## Returns a list of free block in "prefix"
## Allocated should be sorted list
##
def free_blocks(prefix,allocated):
    def boundary(p):
        n,m=p.split("/")
        m=int(m)
        a=address_to_int(n)
        b=bits_to_int(m)
        return (a&b,a|(0xFFFFFFFFL^b))
    # Return a minimal list of prefixes coverting f and t addresses
    def cover_blocks(f,t,b=[]):
        def rank(i):
            j=32
            n=1
            while (i&n)==0 and j:
                j-=1
                n=(n<<1)|1
            return j
        n=rank(f)
        while True:
            size=bits_to_size(n)
            if t-f==size-1:
                return b+[int_to_address(f)+"/%d"%n]
            elif n==32 or t-f>size-1:
                return cover_blocks(f+size,t,b+[int_to_address(f)+"/%d"%n])
            n+=1
    if not allocated:
        # No allocations given. Return whole block
        return [prefix]
    used=[]
    p0,p1=boundary(prefix)
    for a in allocated:
        a0,a1=boundary(a)
        if a0<p0 or a1>p1:
            continue
        if used and a0-used[-1]==1:
            # Merge adjanced allocations
            used[-1]=a1
        else:
            used+=[a0,a1]
    free=[]
    while used:
        u0=used.pop(0)
        u1=used.pop(0)
        free+=[u0-1,u1+1]
    if p0<free[0]:
        free.insert(0,p0)
    else:
        free.pop(0)
    if p1>free[-1]:
        free+=[p1]
    else:
        free.pop(-1)
    r=[]
    while free:
        f=free.pop(0)
        t=free.pop(0)
        r+=cover_blocks(f,t)
    return r
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
if __name__ == "__main__":
    import doctest
    doctest.testmod()
