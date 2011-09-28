# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## lib/ip tests
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from unittest import TestCase
from noc.lib.ip import *

##
## Test for IP
##
class IPTestCase(TestCase):
    def test_prefix(self):
        self.assertEquals(repr(IP.prefix("192.168.0.1")),"<IPv4 192.168.0.1/32>")
        self.assertEquals(repr(IP.prefix("::/0")),"<IPv6 ::/0>")
        self.assertEquals(repr(IP.prefix("2001:db8::/32")),"<IPv6 2001:db8::/32>")
        self.assertEquals(repr(IP.prefix("::ffff:192.168.0.1")),"<IPv6 ::ffff:192.168.0.1/128>")
    
    def test_in(self):
        self.assertEquals("192.168.0.0/24" in IPv4("192.168.0.0/24"), True)
        self.assertEquals(IPv4("192.168.0.0/24") in IPv4("192.168.0.0/24"), True)
        self.assertEquals("192.168.1.1" in IPv4("192.168.0.0/24"), False)
        self.assertEquals(IPv4("192.168.1.1") in IPv4("192.168.0.0/24"), False)
        self.assertRaises(ValueError, lambda: "::1" in IPv4("192.168.0.0/24"))


##
## Test for PrefixDB
##
class PrefixDBTestCase(TestCase):
    def test_set_get_v4(self):
        db=PrefixDB()
        db[IPv4("192.168.0.0/24")]=1
        db[IPv4("192.168.1.0/24")]=2
        db[IPv4("192.168.2.0/24")]=3
        db[IPv4("10.0.0.0/8")]=4
        self.assertEquals(db[IPv4("192.168.0.0/24")],1)
        self.assertEquals(db[IPv4("192.168.1.0/24")],2)
        self.assertEquals(db[IPv4("192.168.2.0/24")],3)
        self.assertEquals(db[IPv4("10.0.0.0/8")],4)

    def test_set_get_v6(self):
        db=PrefixDB()
        db[IPv6("2001:db8:100::/48")]=1
        db[IPv6("2001:db8:200::/48")]=2
        db[IPv6("2001:db8:300::/48")]=3
        db[IPv6("2001:db8:400::/48")]=4
        self.assertEquals(db[IPv6("2001:db8:100::/48")],1)
        self.assertEquals(db[IPv6("2001:db8:200::/48")],2)
        self.assertEquals(db[IPv6("2001:db8:300::/48")],3)
        self.assertEquals(db[IPv6("2001:db8:400::/48")],4)
    

##
## Tests for IPv4
##
class IPv4TestCase(TestCase):
    def test_str(self):
        # Fully qualified
        self.assertEquals(str(IPv4("192.168.0.0/24")),"192.168.0.0/24")
        # Address only
        self.assertEquals(str(IPv4("192.168.0.0")),"192.168.0.0/32")
        # Fully qualified
        self.assertEquals(unicode(IPv4("192.168.0.0/24")),u"192.168.0.0/24")
        # Address only
        self.assertEquals(unicode(IPv4("192.168.0.0")),u"192.168.0.0/32")
        # Netmask
        self.assertEquals(unicode(IPv4("192.168.0.0", netmask="255.255.255.0")),
                          u"192.168.0.0/24")
        
    
    def test_repr(self):
        self.assertEquals(repr(IPv4("192.168.0.0/24")),"<IPv4 192.168.0.0/24>")
    
    def test_len(self):
        self.assertEquals(len(IPv4("192.168.0.0/24")),24)
        self.assertEquals(len(IPv4("192.168.0.0")),32)
        self.assertEquals(len(IPv4("0.0.0.0/0")),0)
    
    CMP=[
        #    Prefix1          Prefix2      cmp    =     !=      <     <=     >     >=
        ("192.168.0.0/24","192.168.0.0/24",  0, True,  False, False, True,  False, True),
        ("192.168.0.0/24","192.168.1.0/24", -1, False, True,  True,  True,  False, False),
        ("192.168.1.0/24","192.168.0.0/24",  1, False, True,  False, False, True,  True),
        ("192.168.0.0/24","192.168.0.0/25", -1, False, True,  True,  True,  False, False),
        ("0.0.0.0/0",     "192.168.0.0/24", -1, False, True,  True,  True,  False, False),
        ("0.0.0.0/0",     "0.0.0.0/1",      -1, False, True,  True,  True,  False, False),
    ]
    def test_comparison(self):
        for p1,p2,c,eq,ne,lt,le,gt,ge in self.CMP:
            p1=IPv4(p1)
            p2=IPv4(p2)
            self.assertEquals(cmp(p1,p2),c,"cmp(%s,%s) failed. Expected %s. Got %s"%(p1,p2,c,cmp(p1,p2)))
            self.assertEquals(p1==p2,eq,"%s == %s failed. Expected %s. Got %s"%(p1,p2,eq,p1==p2))
            self.assertEquals(p1!=p2,ne,"%s != %s failed. Expected %s. Got %s"%(p1,p2,ne,p1!=p2))
            self.assertEquals(p1<p2,lt,"%s < %s failed. Expected %s. Got %s"%(p1,p2,lt,p1<p2))
            self.assertEquals(p1>p2,gt,"%s > %s failed. Expected %s. Got %s"%(p1,p2,gt,p1>p2))
            self.assertEquals(p1<=p2,le,"%s <= %s failed. Expected %s. Got %s"%(p1,p2,le,p1<=p2))
            self.assertEquals(p1>=p2,ge,"%s >= %s failed. Expected %s. Got %s"%(p1,p2,ge,p1>=p2))
    
    def test_hash(self):
        p0=IPv4("192.168.0.1")
        p1=IPv4("192.168.0.2")
        s=set([p0])
        self.assertEquals(p0 in s,True)
        self.assertEquals(p1 in s,False)
        s={p0: True}
        self.assertEquals(s[p0], True)
    
    def test_add(self):
        self.assertEquals(repr(IPv4("0.0.0.0/32")+1),"<IPv4 0.0.0.1/32>")
        self.assertEquals(repr(IPv4("192.168.0.0/32")+257),"<IPv4 192.168.1.1/32>")
        self.assertEquals(repr(IPv4("255.255.255.255/32")+2),"<IPv4 0.0.0.1/32>")
    
    def test_sub(self):
        # prefix - number returns prefix
        self.assertEquals(repr(IPv4("192.168.0.10/32")-9),"<IPv4 192.168.0.1/32>")
        self.assertEquals(repr(IPv4("192.168.1.10/32")-265),"<IPv4 192.168.0.1/32>")
        self.assertEquals(repr(IPv4("0.0.0.0/32")-1),"<IPv4 255.255.255.255/32>")
        
        # prefix - prefix returns distance
        self.assertEquals(IPv4("192.168.0.10/32")-IPv4("192.168.0.1/32"),9)

    def test_iter_bits(self):
        self.assertEquals(list(IPv4("0.0.0.0/8").iter_bits()),[0,0,0,0,0,0,0,0])
        self.assertEquals(list(IPv4("10.0.0.0/8").iter_bits()),[0,0,0,0,1,0,1,0])
        self.assertEquals(list(IPv4("224.0.0.0/4").iter_bits()),[1, 1, 1, 0])
        self.assertEquals(list(IPv4("255.255.255.255").iter_bits()),[1]*32)

    def test_from_bits(self):
        self.assertEquals(repr(IPv4.from_bits([1,1,1,1,1,1,1,1])),"<IPv4 255.0.0.0/8>")
        self.assertEquals(repr(IPv4.from_bits([0,0,0,0,1,0,1,0])),"<IPv4 10.0.0.0/8>")
    
    BITS=[
        "192.168.0.1",
        "224.0.0.0/4",
        "192.168.0.0/16",
        "255.255.255.255"
    ]
    
    def test_from_to_bits(self):
        for b in self.BITS:
            p=IPv4(b)
            self.assertEquals(IPv4.from_bits(p.iter_bits()),p)

    def test_iter_cover(self):
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/24").iter_cover(23)], [])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/24").iter_cover(24)],
            ["<IPv4 192.168.0.0/24>"])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/23").iter_cover(24)],
            ["<IPv4 192.168.0.0/24>", "<IPv4 192.168.1.0/24>"])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/22").iter_cover(24)],
            ["<IPv4 192.168.0.0/24>", "<IPv4 192.168.1.0/24>",
             "<IPv4 192.168.2.0/24>", "<IPv4 192.168.3.0/24>"])

    def test_iter_free(self):
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/22").iter_free(["192.168.0.0/27","192.168.1.0/24","192.168.2.0/24"])],
            ["<IPv4 192.168.0.32/27>", "<IPv4 192.168.0.64/26>", "<IPv4 192.168.0.128/25>", "<IPv4 192.168.3.0/24>"])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/24").iter_free(["192.168.0.0/25","192.168.0.128/25"])],
            [])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.0.0/24"])],
            ["<IPv4 192.168.1.0/24>", "<IPv4 192.168.2.0/23>", "<IPv4 192.168.4.0/22>", "<IPv4 192.168.8.0/21>"])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.15.0/24"])],
            ["<IPv4 192.168.0.0/21>", "<IPv4 192.168.8.0/22>", "<IPv4 192.168.12.0/23>", "<IPv4 192.168.14.0/24>"])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.8.0/24"])],
            ["<IPv4 192.168.0.0/21>", "<IPv4 192.168.9.0/24>", "<IPv4 192.168.10.0/23>", "<IPv4 192.168.12.0/22>"])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.6.0/23"])],
            ["<IPv4 192.168.0.0/22>", "<IPv4 192.168.4.0/23>", "<IPv4 192.168.8.0/21>"])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.6.0/24","192.168.7.0/24"])],
            ["<IPv4 192.168.0.0/22>", "<IPv4 192.168.4.0/23>", "<IPv4 192.168.8.0/21>"])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/20").iter_free(["192.168.0.0/24","192.168.6.0/24","192.168.7.0/24","192.168.15.0/24"])],
            ["<IPv4 192.168.1.0/24>", "<IPv4 192.168.2.0/23>", "<IPv4 192.168.4.0/23>", "<IPv4 192.168.8.0/22>", "<IPv4 192.168.12.0/23>", "<IPv4 192.168.14.0/24>"])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/22").iter_free(["192.168.0.0/24","192.168.1.0/24","192.168.2.0/24","192.168.3.0/24"])],
            [])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/24").iter_free([])],
            ["<IPv4 192.168.0.0/24>"])
    
    def test_iter_address(self):
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0").iter_address(count=5)],
            ['<IPv4 192.168.0.0/32>', '<IPv4 192.168.0.1/32>', '<IPv4 192.168.0.2/32>', '<IPv4 192.168.0.3/32>', '<IPv4 192.168.0.4/32>'])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.255").iter_address(count=5)],
            ['<IPv4 192.168.0.255/32>', '<IPv4 192.168.1.0/32>', '<IPv4 192.168.1.1/32>', '<IPv4 192.168.1.2/32>', '<IPv4 192.168.1.3/32>'])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.255").iter_address(until="192.168.1.3")],
            ['<IPv4 192.168.0.255/32>', '<IPv4 192.168.1.0/32>', '<IPv4 192.168.1.1/32>', '<IPv4 192.168.1.2/32>', '<IPv4 192.168.1.3/32>'])
            
    
    def test_size(self):
        self.assertEquals(IPv4("0.0.0.0/0").size, 4294967296)
        self.assertEquals(IPv4("10.0.0.0/8").size, 16777216)
        self.assertEquals(IPv4("192.168.0.0/16").size, 65536)
        self.assertEquals(IPv4("0.0.0.0").size, 1)
    
    def test_contains(self):
        self.assertEquals(IPv4("192.168.0.0/24").contains(IPv4("192.168.0.0/24")), True)
        self.assertEquals(IPv4("192.168.0.0/24").contains(IPv4("192.168.0.0/25")), True)
        self.assertEquals(IPv4("192.168.0.0/24").contains(IPv4("192.168.0.0")), True)
        self.assertEquals(IPv4("192.168.0.0/24").contains(IPv4("192.168.0.127")), True)
        self.assertEquals(IPv4("192.168.0.0/24").contains(IPv4("192.168.0.255")), True)
        self.assertEquals(IPv4("192.168.0.0/24").contains(IPv4("192.167.255.255")), False)
        self.assertEquals(IPv4("192.168.0.0/24").contains(IPv4("192.168.1.0")), False)
    
    def test_first(self):
        self.assertEquals(repr(IPv4("192.168.0.5/24").first), "<IPv4 192.168.0.0/24>")
    
    def test_last(self):
        self.assertEquals(repr(IPv4("192.168.0.5/24").last), "<IPv4 192.168.0.255/24>")
    
    def test_area_spot(self):
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/24").area_spot([],dist=2)], [])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/24").area_spot([],dist=2,sep=True)], [])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/30").area_spot(["192.168.0.1"],dist=16,sep=True)],
            ['<IPv4 192.168.0.1/32>', '<IPv4 192.168.0.2/32>'])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/24").area_spot(["192.168.0.1","192.168.0.2","192.168.0.128"],dist=2)],
            ['<IPv4 192.168.0.1/32>', '<IPv4 192.168.0.2/32>', '<IPv4 192.168.0.3/32>', '<IPv4 192.168.0.4/32>', '<IPv4 192.168.0.126/32>',
                '<IPv4 192.168.0.127/32>', '<IPv4 192.168.0.128/32>', '<IPv4 192.168.0.129/32>', '<IPv4 192.168.0.130/32>'])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/24").area_spot(["192.168.0.1","192.168.0.2","192.168.0.128"],dist=2,sep=True)],
            ['<IPv4 192.168.0.1/32>', '<IPv4 192.168.0.2/32>', '<IPv4 192.168.0.3/32>', '<IPv4 192.168.0.4/32>', "None",
            '<IPv4 192.168.0.126/32>','<IPv4 192.168.0.127/32>', '<IPv4 192.168.0.128/32>', '<IPv4 192.168.0.129/32>', '<IPv4 192.168.0.130/32>'])
        self.assertEquals([repr(x) for x in IPv4("192.168.0.0/24").area_spot(["192.168.0.1","192.168.0.254"],dist=2,sep=True)],
            ['<IPv4 192.168.0.1/32>', '<IPv4 192.168.0.2/32>', '<IPv4 192.168.0.3/32>', 'None', '<IPv4 192.168.0.252/32>',
            '<IPv4 192.168.0.253/32>', '<IPv4 192.168.0.254/32>'])
    
    def test_normalized(self):
        self.assertEquals(repr(IPv4("192.168.0.1/24").normalized), '<IPv4 192.168.0.0/24>')
        self.assertEquals(repr(IPv4("239.12.5.15/4").normalized), '<IPv4 224.0.0.0/4>')
    
    def test_set_mask(self):
        self.assertEquals(repr(IPv4("192.168.0.5/24").set_mask()), '<IPv4 192.168.0.5/32>')
        self.assertEquals(repr(IPv4("192.168.0.5/24").set_mask(25)), '<IPv4 192.168.0.5/25>')
    
    def test_netmask(self):
        self.assertEquals(repr(IPv4("192.168.0.0/24").netmask), '<IPv4 255.255.255.0/32>')
        self.assertEquals(repr(IPv4("192.168.0.0/30").netmask), '<IPv4 255.255.255.252/32>')
    
    def test_wildcard(self):
        self.assertEquals(repr(IPv4("192.168.0.0/24").wildcard), '<IPv4 0.0.0.255/32>')
        self.assertEquals(repr(IPv4("192.168.0.0/30").wildcard), '<IPv4 0.0.0.3/32>')
    
    def test_rebase(self):
        # prefix, base, new base, result
        data=[
            ("192.168.0.0/24", "192.168.0.0/24", "192.168.1.0/24", "192.168.1.0/24"),
            ("192.168.0.0/25", "192.168.0.0/24", "192.168.1.0/24", "192.168.1.0/25"),
            ("192.168.0.128/25", "192.168.0.0/24", "192.168.1.0/24", "192.168.1.128/25"),
            ("192.168.0.130/32", "192.168.0.0/24", "192.168.1.0/24", "192.168.1.130/32"),
            ("192.168.0.130/32", "192.168.0.128/25", "192.168.1.0/24", "192.168.1.2/32"),
        ]
        
        for p, b, nb, r in data:
            self.assertEquals(IPv4(p).rebase(IPv4(b), IPv4(nb)), IPv4(r))
    
    def test_netmask_to_len(self):
        data = [
            ("0.0.0.0", 0),
            ("255.0.0.0", 8),
            ("255.255.0.0", 16),
            ("255.255.255.0", 24),
            ("255.255.255.255", 32),
            ("128.0.0.0", 1),
            ("255.255.192.0", 18)
        ]
        
        for m, b in data:
            self.assertEquals(IPv4.netmask_to_len(m), b, "%s != /%d" % (m, b))


##
## IPv6 Prefix unittests
##
class IPv6TestCase(TestCase):
    def test_str(self):
        # Fully qualified
        self.assertEquals(str(IPv6("::/0")),"::/0")
        self.assertEquals(str(IPv6("2001:db8::/32")),"2001:db8::/32")
        self.assertEquals(str(IPv6("::ffff:192.168.0.1")),"::ffff:192.168.0.1/128")
        # Address only
        self.assertEquals(str(IPv6("::")),"::/128")
        # Fully qualified
        self.assertEquals(unicode(IPv6("::/0")),u"::/0")
        self.assertEquals(unicode(IPv6("2001:db8::/32")),u"2001:db8::/32")
        self.assertEquals(unicode(IPv6("::ffff:192.168.0.1")),u"::ffff:192.168.0.1/128")
        # Address only
        self.assertEquals(unicode(IPv6("::")),u"::/128")


    def test_repr(self):
        self.assertEquals(repr(IPv6("::")),"<IPv6 ::/128>")

    def test_len(self):
        self.assertEquals(len(IPv6("::/0")),0)
        self.assertEquals(len(IPv6("::")),128)
        self.assertEquals(len(IPv6("2001:db8::/32")),32)
        self.assertEquals(len(IPv6("::ffff:19.168.0.1")),128)

    CMP=[
        #    Prefix1     Prefix2 cmp    =     !=      <     <=     >     >=
        ("100::/16", "100::/16",  0, True,  False, False, True,  False, True),
        ("100::/16", "200::/16", -1, False, True,  True,  True,  False, False),
        ("200::/16", "100::/16",  1, False, True,  False, False, True,  True),
        ("100::/16", "100::/32", -1, False, True,  True,  True,  False, False),
        ("::/0",     "100::/16", -1, False, True,  True,  True,  False, False),
        ("::/0",     "::/1",     -1, False, True,  True,  True,  False, False),
        ("100:200:300:400::/64",
         "100:200:300:200::/64",  1, False, True,  False,  False,  True, True),
        ("100:200:300:200::/64",
         "100:200:300:400::/64",-1, False, True,  True,  True,  False, False),
        ("::100:200:300:400/64",
         "::100:200:300:200/64",  1, False, True,  False,  False,  True, True),
        ("::100:200:300:200/64",
         "::100:200:300:400/64",-1, False, True,  True,  True,  False, False),
        ("::100:200:300:400/64",
         "::100:100:300:400/64",  1, False, True,  False,  False,  True, True),
        ("::100:100:300:400/64",
         "::100:200:300:400/64",-1, False, True,  True,  True,  False, False),
        
    ]
    def test_comparison(self):
        for p1,p2,c,eq,ne,lt,le,gt,ge in self.CMP:
            p1=IPv6(p1)
            p2=IPv6(p2)
            self.assertEquals(cmp(p1,p2),c,"cmp(%s,%s) failed. Expected %s. Got %s"%(p1,p2,c,cmp(p1,p2)))
            self.assertEquals(p1==p2,eq,"%s == %s failed. Expected %s. Got %s"%(p1,p2,eq,p1==p2))
            self.assertEquals(p1!=p2,ne,"%s != %s failed. Expected %s. Got %s"%(p1,p2,ne,p1!=p2))
            self.assertEquals(p1<p2,lt,"%s < %s failed. Expected %s. Got %s"%(p1,p2,lt,p1<p2))
            self.assertEquals(p1>p2,gt,"%s > %s failed. Expected %s. Got %s"%(p1,p2,gt,p1>p2))
            self.assertEquals(p1<=p2,le,"%s <= %s failed. Expected %s. Got %s"%(p1,p2,le,p1<=p2))
            self.assertEquals(p1>=p2,ge,"%s >= %s failed. Expected %s. Got %s"%(p1,p2,ge,p1>=p2))
            

    def test_hash(self):
        p0=IPv6("::1")
        p1=IPv6("::2")
        s=set([p0])
        self.assertEquals(p0 in s,True)
        self.assertEquals(p1 in s,False)
        s={p0: True}
        self.assertEquals(s[p0], True)

    def test_add(self):
        self.assertEquals(repr(IPv6("::/128")+1),"<IPv6 ::1/128>")
        self.assertEquals(repr(IPv6("::/128")+0xffffffff),"<IPv6 ::ffff:ffff/128>")
        self.assertEquals(repr(IPv6("::1/128")+0xffffffff),"<IPv6 ::1:0:0/128>")
        self.assertEquals(repr(IPv6("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff")+2),"<IPv6 ::1/128>")

    def test_sub(self):
        # prefix - number returns prefix
        self.assertEquals(repr(IPv6("100::5")-3),"<IPv6 100::2/128>")
        self.assertEquals(repr(IPv6("100::5")-5),"<IPv6 100::/128>")
        self.assertEquals(repr(IPv6("100::5")-6),"<IPv6 ff:ffff:ffff:ffff:ffff:ffff:ffff:ffff/128>")
        # prefix - prefix returns distance
        self.assertEquals(IPv6("100::7")-IPv6("100::5"),2)

    def test_iter_bits(self):
        self.assertEquals(list(IPv6("::/16").iter_bits()),[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEquals(list(IPv6("ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff").iter_bits()),[1]*128)
        self.assertEquals(list(IPv6("f000::/4").iter_bits()),[1, 1, 1, 1])
    
    def test_from_bits(self):
        self.assertEquals(repr(IPv6.from_bits([1,1,1,1,1,1,1,1])),"<IPv6 ff00::/8>")
        self.assertEquals(repr(IPv6.from_bits([1,1,1,1,1,1,1,1,1])),"<IPv6 ff80::/9>")
        
    BITS=[
        "::",
        "::ffff:192.168.0.1",
        "2001:db8::/32",
        "100::1"
    ]
    def test_from_to_bits(self):
        for b in self.BITS:
            p=IPv6(b)
            self.assertEquals(IPv6.from_bits(p.iter_bits()),p)
    
    def test_iter_free(self):
        self.assertEquals([repr(x) for x in IPv6("2001:db8::/32").iter_free([])],
            ["<IPv6 2001:db8::/32>"])
        self.assertEquals([repr(x) for x in IPv6("2001:db8::/32").iter_free(["2001:db8::/34"])],
            ['<IPv6 2001:db8:4000::/34>', '<IPv6 2001:db8:8000::/33>'])
        self.assertEquals([repr(x) for x in IPv6("2001:db8::/32").iter_free(["2001:db8:4000::/34"])],
            ['<IPv6 2001:db8::/34>', '<IPv6 2001:db8:8000::/33>'])

    def test_iter_address(self):
        self.assertEquals([repr(x) for x in IPv6("2001:db8::").iter_address(count=5)],
            ['<IPv6 2001:db8::/128>', '<IPv6 2001:db8::1/128>', '<IPv6 2001:db8::2/128>', '<IPv6 2001:db8::3/128>', '<IPv6 2001:db8::4/128>'])
        self.assertEquals([repr(x) for x in IPv6("2001:db8::ffff").iter_address(count=5)],
            ['<IPv6 2001:db8::ffff/128>', '<IPv6 2001:db8::1:0/128>', '<IPv6 2001:db8::1:1/128>', '<IPv6 2001:db8::1:2/128>', '<IPv6 2001:db8::1:3/128>'])
        self.assertEquals([repr(x) for x in IPv6("2001:db8::ffff").iter_address(until='2001:db8::1:3')],
            ['<IPv6 2001:db8::ffff/128>', '<IPv6 2001:db8::1:0/128>', '<IPv6 2001:db8::1:1/128>', '<IPv6 2001:db8::1:2/128>', '<IPv6 2001:db8::1:3/128>'])
            
    
    def test_contains(self):
        self.assertEquals(IPv6("2001:db8::/32").contains(IPv6("2001:db8::/32")), True)
        self.assertEquals(IPv6("2001:db8::/32").contains(IPv6("2001:db8::/64")), True)
        self.assertEquals(IPv6("2001:db8::/32").contains(IPv6("2001:db8::")), True)
        self.assertEquals(IPv6("2001:db8::/32").contains(IPv6("2001:db8:0:ffff:ffff:ffff:ffff:ffff")), True)
        self.assertEquals(IPv6("2001:db8::/32").contains(IPv6("2001:db8:ffff:ffff:ffff:ffff:ffff:ffff")), True)
        self.assertEquals(IPv6("2001:db8::/32").contains(IPv6("2001:db7:ffff:ffff:ffff:ffff:ffff:ffff")), False)
        self.assertEquals(IPv6("2001:db8::/32").contains(IPv6("2001:db9::")), False)
    
    def test_area_spot(self):
        self.assertEquals([repr(x) for x in IPv6("2001:db8::/32").area_spot(["2001:db8::1","2001:db8::a"],dist=2)],
            ['<IPv6 2001:db8::/128>', '<IPv6 2001:db8::1/128>', '<IPv6 2001:db8::2/128>', '<IPv6 2001:db8::3/128>',
            '<IPv6 2001:db8::8/128>', '<IPv6 2001:db8::9/128>', '<IPv6 2001:db8::a/128>', '<IPv6 2001:db8::b/128>',
            '<IPv6 2001:db8::c/128>'])
    
    def test_first(self):
        self.assertEquals(repr(IPv6("2001:db8::10/32").first), "<IPv6 2001:db8::/32>")
    
    def test_last(self):
        self.assertEquals(repr(IPv6("2001:db8::10/32").last), "<IPv6 2001:db8:ffff:ffff:ffff:ffff:ffff:ffff/32>")

    def test_normalized(self):
        self.assertEquals(repr(IPv6("0:00:0:0:0::1").normalized), "<IPv6 ::1/128>")
        self.assertEquals(repr(IPv6("2001:db8:0:7:0:0:0:1").normalized), "<IPv6 2001:db8:0:7::1/128>")
        self.assertEquals(repr(IPv6("::ffff:c0a8:1").normalized), "<IPv6 ::ffff:192.168.0.1/128>")
    
    def test_set_mask(self):
        self.assertEquals(repr(IPv6("2001:db8::20/48").set_mask()), "<IPv6 2001:db8::20/128>")
        self.assertEquals(repr(IPv6("2001:db8::20/48").set_mask(64)), "<IPv6 2001:db8::20/64>")
    
    def test_ptr(self):
        self.assertEquals(IPv6("2001:db8::1").ptr(0), "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2")
        self.assertEquals(IPv6("2001:db8::1").ptr(8), "1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0")
    
    def test_digits(self):
        self.assertEquals(IPv6("2001:db8::1").digits, ["2","0","0","1","0","d","b","8","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","0","1"])
    
    def test_rebase(self):
        # prefix, base, new base, result
        data=[
            ("2001:db8::7/128", "2001:db8::/32", "2001:db9::/32", "2001:db9::7/128"),
        ]
        
        for p, b, nb, r in data:
            self.assertEquals(IPv6(p).rebase(IPv6(b), IPv6(nb)), IPv6(r))

