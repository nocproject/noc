##
## This file is a part of Effortel's NOC db project
##
import re
from django.forms import ValidationError
##
## Validators returning boolean
##
def is_int(v):
    try:
        v=int(v)
    except:
        return False
    return True
    
def is_asn(v):
    try:
        v=int(v)
    except:
        return False
    return 0<=v<=65535

def is_ipv4(v):
    X=v.split(".")
    if len(X)!=4:
        return False
    try:
        return len([x for x in X if 0<=int(x)<=255])==4
    except:
        return False
    
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
    
rx_asset=re.compile(r"^AS-[A-Z0-9\-]+$")
def is_as_set(v):
    return rx_asset.match(v) is not None

rx_fqdn=re.compile(r"^([a-z0-9\-]+\.)+[a-z0-9\-]+$",re.IGNORECASE)
def is_fqdn(v):
    return rx_fqdn.match(v) is not None
    
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