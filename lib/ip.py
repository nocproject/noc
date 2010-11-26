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
    def iter_address(self,count=None,until=None,filter=None):
        if until and isinstance(until,basestring):
            until=self.__class__(until)
        if until:
            until+=1
        n=0
        a=self
        while True:
            if filter is None or filter(a):
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
        spot_size=2*dist+1
        s_first=self.first.set_mask()
        s_last=self.last.set_mask()
        # Return all addresses except network and broadcast
        # for IPv4, when a dist is larger than network size
        if self.afi=="4" and dist>=self.size:
            d=0 if s_first.address in addresses else 1
            return list((s_first+d).iter_address(until=s_last-1))
        # Left only addresses remaining in prefix and convert them to
        # IP instances
        addresses=set([a for a in [IP.prefix(a) if isinstance(a,basestring) else a for a in addresses] if self.contains(a)])
        addresses=sorted(addresses)
        # Fill the spot
        spot=[]
        last=None
        last_touched=None
        for a in addresses:
            # Fill spot around the first address
            if last is None:
                last_touched=min(a+dist,s_last)
                spot=list(max(a-dist,s_first).iter_address(until=last_touched))
            else:
                d=a-last
                if d<=dist:
                    # No gap, fill d addresses from last touched
                    lt=min(last_touched+d,s_last)
                    spot+=list((last_touched+1).iter_address(until=lt))
                else:
                    # Gap, insert separator if needed
                    if sep:
                        spot+=[None]
                    # Fill spot around address
                    lt=min(a+dist,s_last)
                    spot+=list((a-dist).iter_address(until=lt))
                last_touched=lt
            # Exit if last address touched
            if last_touched==s_last:
                break
            last=a
        # Return result
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
    ## Returns new IPv4 instance in normalized minimal possible form
    ##
    @property
    def normalized(self):
        return self._to_prefix(self.d&((1L<<self.mask)-1L)<<(32L-self.mask),self.mask)
    
    ##
    ## Returns new IPv4 instance with new mask value.
    ## If mask not set, returns with /32
    ##
    def set_mask(self,mask=None):
        return self._to_prefix(self.d,32 if mask is None else mask)
    

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
        if len(parts)==8:
            parts=[p if p else "0" for p in parts]
        else:
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
    ## Returns new IPv4 instance with new mask value.
    ## If mask not set, returns with /128
    ##
    def set_mask(self,mask=None):
        return self._to_prefix(self.d0,self.d1,self.d2,self.d3,128 if mask is None else mask)
    
    #
    # Returns 32 hexadecimal digits
    #
    @property
    def digits(self):
        return list("".join(["%08x"%self.d0,"%08x"%self.d1,"%08x"%self.d2,"%08x"%self.d3]))
    
    #
    # Returns PTR value for IPv6 reverse zone
    #
    def ptr(self,origin_len):
        r=self.digits[origin_len:]
        r.reverse()
        return ".".join(r)
    

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
    

