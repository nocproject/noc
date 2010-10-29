# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IP address manipulation routines
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.validators import *

#
B16=0xffffL
B32=0xffffffffL
##
## Base class for IP prefix
##
class IP(object):
    afi=None
    def __init__(self,prefix):
        self.prefix=prefix
        self.address,self.mask=prefix.split("/")
        self.mask=int(self.mask)
    
    ##
    ## String representation
    ##
    def __repr__(self):
        return "<IPv%s %s>"%(self.afi,self.prefix)
    
    ##
    ## Return prefix as string
    ##
    def __str__(self):
        return self.prefix
    
    ##
    ## Return prefix as unicode
    ##
    def __unicode__(self):
        return self.prefix
    
    ##
    ## Return mask length
    ##
    def __len__(self):
        return self.mask
    
    ##
    ## cmp()
    ##
    def __cmp__(self,other):
        if self==other:
            return 0
        if self<other:
            return -1
        return 1
    
    ##
    ## <= operator
    ##
    def __le__(self, other):
        return self==other or self<other
    
    ##
    ## >= operator
    ##
    def __ge__(self,other):
        return self==other or self>other
    
    ##
    ## Accept arbitraty IPv4/IPv6 prefix in the string
    ## and return proper IPv4 or IPv6 instance
    ##
    @classmethod
    def prefix(cls,prefix):
        if ":" in prefix:
            return IPv6(prefix)
        else:
            return IPv4(prefix)
    
    ##
    ## Generator returning continuing set of addresses
    ##
    def iter_address(self,count=None,until=None):
        if until and isinstance(until,basestring):
            until=self.__class__(until)
        if until:
            until+=1
        n=0
        a=self
        while True:
            yield a
            a+=1
            n+=1
            if (count and n>=count) or (until and a==until):
                raise StopIteration
    
    ##
    ## Generator returning free prefixes
    ##
    def iter_free(self,prefixes):
        # Fill Tree
        db=PrefixDB()
        n=0
        for p in prefixes:
            if isinstance(p,basestring):
                p=self.__class__(p)
            db[p]=True
            n+=1
        if n==0:
            yield self
            raise StopIteration
        #
        for p in db.iter_free(self):
            yield p
    
    ##
    ## Returns a list of addresses, laying inside prefix and containing area
    ## aroung given addresses
    ## When sep is True, None will be added between non-continous addresses
    ##
    def area_spot(self,addresses,dist,sep=False):
        if not addresses:
            return []
        spot=set()
        spot_size=2*dist+1
        if self.afi=="4" and dist>=self.size:
            return list((self.first+1).iter_address(until=self.last-1))
        for a in addresses:
            if isinstance(a,basestring):
                a=IP.prefix(a)
            if not self.contains(a):
                continue
            for sa in (a-dist).iter_address(count=spot_size):
                if sa not in spot and self.contains(sa):
                    spot.add(sa)
        spot=sorted(spot)
        if sep:
            s0=spot.pop(0)
            s=[s0]
            while spot:
                s1=spot.pop(0)
                if s1!=(s0+1):
                    s+=[None]
                s+=[s1]
                s0=s1
            spot=s
        if self.afi=="4":
            # Remove network and broadcast address
            return [a for a in spot if a is None or a.address not in (self.first.address,self.last.address)]
        else:
            return spot
    

##
## IPv4 prefix
## Internally stored as unsigned 32-bit integer
##
class IPv4(IP):
    afi="4"
    def __init__(self,prefix):
        if "/" not in prefix:
            prefix+="/32"
        check_ipv4_prefix(prefix)
        super(IPv4,self).__init__(prefix)
        # Convert to int
        self.d=0L
        m=24
        for d in self._get_parts():
            self.d+=d<<m
            m-=8
    
    ##
    ## Returns a list of 4 integers (IPv4 octets)
    ##
    def _get_parts(self):
        return [int(d) for d in self.address.split(".")]
    
    ##
    ## Convert 32-bit integer and mast into new IPv4 instance
    ##
    @classmethod
    def _to_prefix(cls,s,mask):
        return IPv4("%d.%d.%d.%d/%d"%((s>>24)&0xff,(s>>16)&0xff,(s>>8)&0xff,s&0xff,mask))
    
    ##
    ## Hashing function
    ##
    def __hash__(self):
        return self.d
    
    ##
    ## == operator
    ##
    def __eq__(self,other):
        return self.d==other.d and self.mask==other.mask
    
    ##
    ## != operator
    ##
    def __ne__(self,other):
        return self.d!=other.d or self.mask!=other.mask
    
    ##
    ## < operator
    ##
    def __lt__(self, other):
        return self.d<other.d or (self.d==other.d and self.mask<other.mask)
    
    ##
    ## > operator
    ##
    def __gt__(self, other):
        return self.d>other.d or (self.d==other.d and self.mask>other.mask)
    
    ##
    ## + operator. Second argument is an integer
    ##
    def __add__(self,n):
        return self._to_prefix((self.d+n)&B32,self.mask)
    
    ##
    ## - operator. Second argument is and integer or IPv4 instance
    ## If second argument is integer - returns new IPv4 instance
    ## IP IPv4 instance - returns a distance between addresses
    ##
    def __sub__(self,n):
        if isinstance(n,IPv4):
            return self.d-n.d
        else:
            d=self.d-n
            if d<0:
                d=B32+self.d
            return self._to_prefix(d,self.mask)
    
    ##
    ## Generator returning mask bits of prefix
    ##
    def iter_bits(self):
        m= 1L<<31
        for i in range(self.mask):
            yield 1 if self.d&m else 0
            m>>=1
    
    ##
    ## Convert list of bits to a new IPv4 instance
    ##
    @classmethod
    def from_bits(cls,bits):
        d=0
        n=0
        for b in bits:
            d=(d<<1)|b
            n+=1
        if n<32:
            d<<=(32-n)
        return cls._to_prefix(d,n)
    
    ##
    ## Return IPv4 prefix size (number of addresses to hold)
    ##
    @property
    def size(self):
        return 2**(32-self.mask)
    
    ##
    ## Returns new IPv4 instance with first address of the block (network)
    ##
    @property
    def first(self):
        return self._to_prefix(self.d&(((1L<<self.mask)-1L)<<(32L-self.mask)),self.mask)
    
    ##
    ## Returns new IPv4 instance with last address of the block (broadcast)
    ##
    @property
    def last(self):
        return self._to_prefix(self.d|(B32^(((1L<<self.mask)-1L)<<(32L-self.mask))),self.mask)
    
    ##
    ## Returns new IPv4 instance holding netmask
    ##
    @property
    def netmask(self):
        return self._to_prefix(((1L<<self.mask)-1L)<<(32L-self.mask),32)
    
    ##
    ## Returns new IPv4 instance with Cisco-style wildcard
    ##
    @property
    def wildcard(self):
        return self._to_prefix((2**(32-self.mask))-1,32)
    
    ##
    ## Check if *other* contained in prefix. Returns bool
    ##
    def contains(self,other):
        if self.mask>other.mask:
            return False
        m=((1L<<self.mask)-1L)<<(32L-self.mask)
        return (self.d&m)==(other.d&m)

##
## IPv6 prefix
## Internally stored as four 32-bit integers
##
class IPv6(IP):
    afi="6"
    def __init__(self,prefix):
        if "/" not in prefix:
            prefix+="/128"
        check_ipv6_prefix(prefix)
        super(IPv6,self).__init__(prefix)
        # Convert to 4 ints
        p=self._get_parts()
        self.d0=(p[0]<<16)+p[1]
        self.d1=(p[2]<<16)+p[3]
        self.d2=(p[4]<<16)+p[5]
        self.d3=(p[6]<<16)+p[7]
    
    ##
    ## Convert prefix to a list of 8 integers
    ##
    def _get_parts(self):
        if self.address=="::":
            return [0,0,0,0,0,0,0,0]
        parts=self.address.split(":")
        if "." in parts[-1]:
            p=[int(x) for x in parts[-1].split(".")]
            parts=parts[:-1]+["%02x%02x"%(p[0],p[1]),"%02x%02x"%(p[2],p[3])]
        if len(parts)<8:
            # Expand ::
            i=parts.index("")
            h=[]
            t=[]
            if i>0:
                h=parts[:i]
            if i+1<len(parts) and not parts[i+1]:
                i+=1
            t=parts[i+1:]
            parts=h+["0"]*(8-len(h)-len(t))+t
        return [int(p,16) for p in parts]
    
    ##
    ## Return 4 integers, containing bit mask
    ##
    def _get_masks(self):
        masks=[]
        mask=self.mask
        while mask:
            if mask>=32:
                masks+=[0xffffffff]
                mask-=32
            else:
                masks+=[((1L<<mask)-1L)<<(32L-mask)]
                mask=0
        masks+=[0]*(4-len(masks))
        return masks
    
    ##
    ## Convert four 32-bit integers and mask to a new IPv6 instance
    ##
    @classmethod
    def _to_prefix(cls,d0,d1,d2,d3,mask):
        r=[(d0>>16)&B16, d0&B16, (d1>>16)&B16, d1&B16, (d2>>16)&B16, d2&B16, (d3>>16)&B16, d3&B16]
        # Format groups
        if r[:-3]==[0,0,0,0,0] and r[-3]==0xffff:
            return IPv6("::ffff:%d.%d.%d.%d/%d"%(r[-2]>>8,r[-2]&0xff,r[-1]>>8,r[-1]&0xff,mask))
        # Compact longest zeroes sequence
        lp=0
        ll=0
        cp=0
        while True:
            try:
                i=r.index(0,cp)
            except ValueError:
                break
            s=i
            l=1
            while s+l<len(r) and r[s+l]==0:
                l+=1
            if l>ll:
                lp=s
                ll=l
            cp=s+l
        if ll:
            h=r[:lp]
            t=r[lp+ll:]
            return IPv6("%s::%s/%d"%(":".join(["%x"%p for p in h]),":".join(["%x"%p for p in t]),mask))
        else:
            return IPv6(":".join(["%x"%p for p in r])+"/%d"%mask)
        
    
    ##
    ## hash(..)
    ##
    def __hash__(self):
        return hash(self.prefix)
    
    ##
    ## == operator
    ##
    def __eq__(self,other):
        return self.d0==other.d0 and self.d1==other.d1 and self.d2==other.d2 and self.d3==other.d3 and self.mask==other.mask
    
    ##
    ## != operator
    ##
    def __ne__(self,other):
        return self.d0!=other.d0 or self.d1!=other.d1 or self.d2!=other.d2 or self.d3!=other.d3 or self.mask!=other.mask
    
    ##
    ## < operator
    ##
    def __lt__(self, other):
        if self.d0!=other.d0:
            return self.d0<other.d0
        if self.d1!=other.d1:
            return self.d1<other.d1
        if self.d2!=other.d2:
            return self.d2<other.d2
        if self.d3==other.d3:
            return self.mask<other.mask
        return self.d3<other.d3
    
    ##
    ## > operator
    ##
    def __gt__(self, other):
        if self.d0!=other.d0:
            return self.d0>other.d0
        if self.d1!=other.d1:
            return self.d1>other.d1
        if self.d2!=other.d2:
            return self.d2>other.d2
        if self.d3==other.d3:
            return self.mask>other.mask
        return self.d3>other.d3
    
    ##
    ## + operator. Second argument is an integer.
    ## Returns new IPv6 instance
    ##
    def __add__(self,n):
        d3=self.d3+n
        d2=self.d2
        d1=self.d1
        d0=self.d0
        if d3>B32:
            d3&=B32
            d2+=1
        if d2>B32:
            d2&=B32
            d1+=1
        if d1>B32:
            d1&=B32
            d0+=1
        if d0>B32:
            d0&=B32
            #d3+=1
        return self._to_prefix(d0,d1,d2,d3,self.mask)
    
    ##
    ## - operator. Second argument is an integer or IPv6 instance
    ## Return new IPv6 instance, if second argument is integer,
    ## or distance betweed two prefixes
    ##
    def __sub__(self,n):
        d3=self.d3
        d2=self.d2
        d1=self.d1
        d0=self.d0
        if isinstance(n,IPv6):
            # Rough 32-bit arithmetic
            return self.d3-n.d3
        else:
            d3-=n
            if d3<0:
                d3=B32+d3+1
                d2-=1
            if d2<0:
                d2=B32+d2+1
                d1-=1
            if d1<0:
                d1=B32+d1+1
                d0-=1
            if d0<0:
                d0=B32+d0+1
                d3-=1
        return self._to_prefix(d0,d1,d2,d3,self.mask)
    
    ##
    ## Generator returning *mask* bits of prefix
    ##
    def iter_bits(self):
        d=[self.d0,self.d1,self.d2,self.d3]
        for i in range(self.mask):
            if i%32==0:
                cd=d.pop(0)
                m=1<<31
            yield 1 if cd&m else 0
            m>>=1
    
    ##
    ## Convert a list of bits to a new IPv6 prefix instance
    ##
    @classmethod
    def from_bits(cls,bits):
        d=[0,0,0,0]
        n=0
        for b in bits:
            d[n//32]=(d[n//32]<<1)|b
            n+=1
        if n%32:
            d[n//32]<<=(32-(n%32))
        return cls._to_prefix(d[0],d[1],d[2],d[3],n)
    
    ##
    ## Check if *other* contained within prefix. Returns bool
    ##
    def contains(self,other):
        if self.mask>other.mask:
            return False
        for a1,a2,m in zip([self.d0,self.d1,self.d2,self.d3],[other.d0,other.d1,other.d2,other.d3],self._get_masks()):
            if not m:
                return True
            if (a1&m) != (a2&m):
                return False
        return True
    
    ##
    ## Returns new IPv6 instance with first address of prefix
    ##
    @property
    def first(self):
        masks=self._get_masks()
        return self._to_prefix(self.d0&masks[0],self.d1&masks[1],self.d2&masks[2],self.d3&masks[3],self.mask)
    
    ##
    ## Returns new IPv6 instance with last address of prefix
    ##
    @property
    def last(self):
        masks=[B32^m for m in self._get_masks()]
        return self._to_prefix(self.d0|masks[0],self.d1|masks[1],self.d2|masks[2],self.d3|masks[3],self.mask)
    
    ##
    ## Returns new IPv6 instance in normalized minimal possible form
    ##
    @property
    def normalized(self):
        return self._to_prefix(self.d0,self.d1,self.d2,self.d3,self.mask)
    

##
## Generalized binary-tree prefix lookup database
##
class PrefixDB(object):
    def __init__(self,key=None):
        self.children=[None,None]
        self.key=key
    
    ##
    ## Get key by prefix
    ##
    def __getitem__(self,prefix):
        node=self
        for n in prefix.iter_bits():
            c=node.children[n]
            if c is None:
                break
            node=c
        if node.key:
            return node.key
        else:
            raise KeyError
    
    ##
    ## Put prefix with key
    ##
    def __setitem__(self,prefix,key):
        node=self
        for n in prefix.iter_bits():
            c=node.children[n]
            if c is None:
                c=self.__class__(node.key)
                node.children[n]=c
            node=c
        node.key=key
    
    ##
    ## Generator returning free blocks
    ##
    def iter_free(self,root):
        def walk_tree(c,root_bits):
            for n,v in enumerate(c.children):
                bits=root_bits+[n]
                if v==None:
                    yield bits
                elif len(bits)<max_bits:
                    nc=c.children[n]
                    if nc.key is None:
                        for f in walk_tree(nc,bits):
                            yield f
        root_bits=list(root.iter_bits())
        afi=root.afi
        max_bits=32 if afi=="4" else 128
        c=self
        for n in root_bits:
            c=c.children[n]
        # walk tree
        for bits in walk_tree(c,root_bits):
            yield root.__class__.from_bits(bits)
    

##
## @todo: Refactor below
##

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
    >>> bits_to_netmask(0)
    '0.0.0.0'
    >>> bits_to_netmask(32)
    '255.255.255.255'
    >>> bits_to_netmask(-1)
    '255.255.255.255'
    >>> bits_to_netmask(33)
    '255.255.255.255'
    """
    try:
        bits=int(bits)
        if bits<0 or bits>32:
            raise Exception
    except:
        return "255.255.255.255"
    return int_to_address(bits_to_int(bits))

##
## Returns amount of addresses into prefix of "bits" length
##
def bits_to_size(bits):
    """
    >>> bits_to_size(0)
    4294967296L
    >>> bits_to_size(32)
    1L
    >>> bits_to_size(24)
    256L
    """
    return 1L<<(32L-bits)
##
## Returns the size of prefix
##
def prefix_to_size(prefix):
    """
    >>> prefix_to_size("10.0.0.0/32")
    1L
    >>> prefix_to_size("10.0.0.0/8")
    16777216L
    >>> prefix_to_size("10.0.0.0/24")
    256L
    """
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
    """
    >>> broadcast("192.168.0.0/24")
    '192.168.0.255'
    >>> broadcast("192.168.0.0/32")
    '192.168.0.0'
    """
    n,m=prefix.split("/")
    m=int(m)
    return int_to_address(address_to_int(n)|(0xFFFFFFFFL^bits_to_int(m)))
##
##
##
def wildcard(prefix):
    """
    >>> wildcard("192.168.0.0/24")
    '0.0.0.255'
    >>> wildcard("192.168.0.0/32")
    '0.0.0.0'
    """
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
## Compare ip1 against ip2
##
def cmp_ip(ip1,ip2):
    """
    >>> cmp_ip("192.168.0.1","192.168.0.1")
    0
    >>> cmp_ip("192.168.0.1","192.168.0.2")
    -1
    >>> cmp_ip("192.168.0.2","192.168.0.1")
    1
    """
    return cmp(address_to_int(ip1),address_to_int(ip2))

##
##
## Generator returing ip addresses in range
##
def generate_ips(ip1,ip2):
    """
    >>> list(generate_ips("192.168.0.0","192.168.0.0"))
    ['192.168.0.0']
    >>> list(generate_ips("192.168.0.0","192.168.0.3"))
    ['192.168.0.0', '192.168.0.1', '192.168.0.2', '192.168.0.3']
    """
    n1=address_to_int(ip1)
    n2=address_to_int(ip2)
    while True:
        yield int_to_address(n1)
        n1+=1
        if n1>n2:
            break
    
