# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Multicast IP to MAC converter
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Django modules
from django import forms
# NOC modules
from noc.main.apps.calculator.calculators import Calculator as CalculatorBase
from noc.sa.interfaces.base import *
##
## Calculator form
##
class CalculatorForm(forms.Form):
    ip=forms.CharField(required=False)
    mac=forms.CharField(required=False)
    
    def clean_ip(self):
        v=self.cleaned_data["ip"]
        if v:
            return IPv4Parameter().form_clean(v)
    
    def clean_mac(self):
        v=self.cleaned_data["mac"]
        if v:
            return MACAddressParameter().form_clean(v)
    

class Calculator(CalculatorBase):
    name="multicast"
    title="Multicast IP to MAC"
    form_class=CalculatorForm
        
    def calculate(self,ip=None,mac=None):
        def mac_ips(mac):
            def g(mac):
                m=[int(x,16) for x in mac.split(":")]
                for i in range(32):
                    yield ".".join([str(x) for x in [224+(i>>1), m[3]|((i&0x1)<<7), m[4], m[5]]])
            r=[]
            for m in g(mac):
                if r:
                    r+=[("",m)]
                else:
                    r+=[("MAC IPs",m)]
            return r
        
        r=[]
        if ip:
            p=[int(x) for x in ip.split(".")]
            mac=[0x1, 0x0, 0x5E, p[1]&0x7F, p[2], p[3]]
            mac=":".join(["%02X"%x for x in mac])
            r=[
                ("IP",  ip),
                ("MAC", mac)
            ]+mac_ips(mac)
        elif mac:
            r=[
                ("MAC", mac)
            ]+mac_ips(mac)
        return r
