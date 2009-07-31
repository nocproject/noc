# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Data type validators
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import re
try:
    from django.forms import ValidationError
except:
    pass
##
## Validators returning boolean
##

##
## Check value is valid integer
##
def is_int(v):
    try:
        v=int(v)
    except:
        return False
    return True
##
## Check value is valid 2-byte autonomous system number
##
def is_asn(v):
    try:
        v=int(v)
    except:
        return False
    return 0<=v<=65535
##
## Check value is valid IPv4 address
##
def is_ipv4(v):
    X=v.split(".")
    if len(X)!=4:
        return False
    try:
        return len([x for x in X if 0<=int(x)<=255])==4
    except:
        return False
##
## Check value is valid IPv4 prefix
##
def is_cidr(v):
    x=v.split("/")
    if len(x)!=2:
        return False
    if not is_ipv4(x[0]):
        return False
    try:
        y=int(x[1])
    except:
        return False
    return 0<=y<=32
##
## Check value is valid Route Distinguisher
##
def is_rd(v):
    x=v.split(":")
    if len(x)!=2:
        return False
    a,b=x
    try:
        b=int(b)
    except:
        return False
    if is_asn(a):
        return 0<=b<=16777215
    if is_asn(a):
        return 0<=b<=65535
    return False
##
## Check value is valuid AS-SET
##
rx_asset=re.compile(r"^AS-[A-Z0-9\-]+$")
def is_as_set(v):
    return rx_asset.match(v) is not None
##
## Check value is valid FQDN
##
rx_fqdn=re.compile(r"^([a-z0-9\-]+\.)+[a-z0-9\-]+$",re.IGNORECASE)
def is_fqdn(v):
    return rx_fqdn.match(v) is not None
##
## Check value is valid regular expression
##
def is_re(v):
    try:
        re.compile(v)
        return True
    except:
        return False
##
## Check value is valid VLAN ID
##
def is_vlan(v):
    try:
        v=int(v)
        return v>=1 and v<=4095
    except:
        return False
##
##
##
rx_email=re.compile("^[a-z0-9._\-]+@[a-z0-9\-.]+$",re.IGNORECASE)
def is_email(v):
    return rx_email.match(v)
##
## Validators for forms
##
def generic_validator(value,check,error_msg):
    if not check(value):
        raise ValidationError(error_msg)

def check_asn(field_data,all_data):
    generic_validator(field_data,is_asn,"Invalid ASN")

def check_ipv4(field_data,all_data):
    generic_validator(field_data,is_ipv4,"Invalid IPv4")

def check_cidr(field_data,all_data):
    generic_validator(field_data,is_cidr,"Invalid CIDR")

def check_rd(field_data,all_data):
    generic_validator(field_data,is_rd,"Invalid RD")
    
def check_fqdn(field_data,all_data):
    generic_validator(field_data,is_fqdn,"Invalid FQDN")
    
def check_as_set(field_data,all_data):
    generic_validator(field_data,is_as_set,"Invalid AS-SET")

def check_re(field_data,all_data):
    generic_validator(field_data,is_re,"Invalid Regular Expression")

def check_vlan(field_data,all_data):
    generic_validator(field_data,is_vlan,"Invalid VLAN")

def check_email(field_data,all_data):
    generic_validator(field_data,is_email,"Invalid EMail")
