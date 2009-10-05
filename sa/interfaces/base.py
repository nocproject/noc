# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Abstract script interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re,types,datetime

try:
    from django import forms
except ImportError:
    # No django. Interface.get_form() is meaningless
    pass
##
##
##
class InterfaceTypeError(Exception): pass
##
## Abstract parameter
##
class Parameter(object):
    def __init__(self,required=True,default=None):
        self.required=required
        if default:
            default=self.clean(default)
        self.default=default
    ##
    ## Returns ORParameter
    ##
    def __or__(self,other):
        return ORParameter(self,other)
    ##
    ## Perform input parameter normalization
    ##
    def clean(self,value):
        raise InterfaceTypeError
    ##
    ## Perform input parameter normalization for form fields
    ##
    def form_clean(self,value):
        return self.clean(value)
    ##
    ## Returns an form field object
    ##
    def get_form_field(self):
        return forms.CharField(required=self.required,initial=self.default)
##
##
##
class ORParameter(Parameter):
    """
    >>> ORParameter(IntParameter(),IPParameter()).clean(10)
    10
    >>> ORParameter(IntParameter(),IPParameter()).clean("192.168.1.1")
    '192.168.1.1'
    >>> ORParameter(IntParameter(),IPParameter()).clean("xxx")
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    >>> (IntParameter()|IPParameter()).clean(10)
    10
    >>> (IntParameter()|IPParameter()).clean("192.168.1.1")
    '192.168.1.1'
    >>> (IntParameter()|IPParameter()).clean("xxx")
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    """
    def __init__(self,left,right):
        self.left=left
        self.right=right
    def clean(self,value):
        try:
            v=self.left.clean(value)
            return v
        except InterfaceTypeError:
            pass
        return self.right.clean(value)
##
##
##
class NoneParameter(Parameter):
    """
    >>> NoneParameter().clean(None)
    >>> NoneParameter().clean("None")
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    """
    def __init__(self,required=True):
        super(NoneParameter,self).__init__(required=required)
    def clean(self,value):
        if value is not None:
            raise InterfaceTypeError
        return value
##
##
##
class StringParameter(Parameter):
    """
    >>> StringParameter().clean("Test")
    'Test'
    >>> StringParameter().clean(10)
    '10'
    >>> StringParameter().clean(None)
    'None'
    """
    def clean(self,value):
        try:
            return str(value)
        except:
            raise InterfaceTypeError
##
##
##
class REStringParameter(StringParameter):
    """
    >>> REStringParameter("ex+p").clean("exp")
    'exp'
    >>> REStringParameter("ex+p").clean("exxp")
    'exxp'
    >>> REStringParameter("ex+p").clean("regexp 1")
    'regexp 1'
    >>> REStringParameter("ex+p").clean("ex")
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    """
    def __init__(self,regexp,required=True,default=None):
        super(REStringParameter,self).__init__(required=required,default=default)
        self.rx=re.compile(regexp)

    def clean(self,value):
        v=super(REStringParameter,self).clean(value)
        if not self.rx.search(v):
            raise InterfaceTypeError
        return v
##
##
##
class BooleanParameter(Parameter):
    """
    >>> BooleanParameter().clean(True)
    True
    >>> BooleanParameter().clean(False)
    False
    >>> BooleanParameter().clean("True")
    True
    >>> BooleanParameter().clean("yes")
    True
    >>> BooleanParameter().clean(1)
    True
    >>> BooleanParameter().clean(0)
    False
    >>> BooleanParameter().clean([])
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    """
    def clean(self,value):
        if type(value)==types.BooleanType:
            return value
        if type(value) in [types.IntType,types.LongType]:
            return value!=0
        if type(value) in [types.StringType,types.UnicodeType]:
            return value.lower() in ["true","t","yes","y"]
        raise InterfaceTypeError
##
##
##
class IntParameter(Parameter):
    """
    >>> IntParameter().clean(1)
    1
    >>> IntParameter().clean("1")
    1
    >>> IntParameter().clean("not a number")
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    >>> IntParameter(min_value=10).clean(5)
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    >>> IntParameter(max_value=7).clean(10)
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    """
    def __init__(self,required=True,default=None,min_value=None,max_value=None):
        super(IntParameter,self).__init__(required=required,default=default)
        self.min_value=min_value
        self.max_value=max_value
    def clean(self,value):
        try:
            i=int(value)
        except:
            raise InterfaceTypeError
        if (self.min_value is not None and i<self.min_value) or (self.max_value is not None and i>self.max_value):
            raise InterfaceTypeError
        return i
##
##
##
class ListParameter(Parameter):
    def clean(self,value):
        try:
            return list(value)
        except:
            raise InterfaceTypeError
    
    def form_clean(self,value):
        try:
            return self.clean(eval(value,{},{}))
        except:
            raise InterfaceTypeError
##
##
##
class ListOfParameter(ListParameter):
    def __init__(self,element,required=True,default=None):
        super(ListOfParameter,self).__init__(required=required,default=default)
        self.element=element
        
    def clean(self,value):
        v=super(ListOfParameter,self).clean(value)
        return [self.element.clean(x) for x in v]
##
##
##
class StringListParameter(ListOfParameter):
    def __init__(self,required=True,default=None):
        super(StringListParameter,self).__init__(element=StringParameter(),required=required,default=default)
##
##
##
class DictParameter(Parameter):
    """
    >>> DictParameter(attrs={"i":IntParameter(),"s":StringParameter()}).clean({"i":10,"s":"ten"})
    {'i': 10, 's': 'ten'}
    >>> DictParameter(attrs={"i":IntParameter(),"s":StringParameter()}).clean({"i":"10","s":"ten"})
    {'i': 10, 's': 'ten'}
    """
    def __init__(self,required=True,default=None,attrs=None):
        super(DictParameter,self).__init__(required=required,default=default)
        self.attrs=attrs
    def clean(self,value):
        if type(value)!=types.DictType:
            raise InterfaceTypeError
        if not self.attrs:
            return value
        in_value=value.copy()
        out_value={}
        for a_name,attr in self.attrs.items():
            if a_name not in in_value and attr.required:
                raise InterfaceTypeError("Attribute '%s' required"%a_name)
            if a_name in in_value:
                try:
                    out_value[a_name]=attr.clean(in_value[a_name])
                except InterfaceTypeError:
                    raise InterfaceTypeError("Invalid value for '%s'"%a_name)
                del in_value[a_name]
        for k,v in in_value.items():
            out_value[k]=v
        return out_value
##
##
##
rx_datetime=re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$")
class DateTimeParameter(StringParameter):
    def clean(self,value):
        if isinstance(value,datetime.datetime):
            return value.isoformat()
        if value.lower()=="infinite":
            return datetime.datetime(year=datetime.MAXYEAR,month=1,day=1)
        if rx_datetime.match(value):
            return value
        raise InterfaceTypeError
##
##
##
class IPParameter(StringParameter):
    """
    >>> IPParameter().clean("192.168.0.1")
    '192.168.0.1'
    >>> IPParameter().clean("192.168.0.256")
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    """
    def clean(self,value):
        v=super(IPParameter,self).clean(value)
        X=v.split(".")
        if len(X)!=4:
            raise InterfaceTypeError
        try:
            if len([x for x in X if 0<=int(x)<=255])!=4:
                raise InterfaceTypeError
        except:
            raise InterfaceTypeError
        return v
##
##
##
class VLANIDParameter(IntParameter):
    """
    >>> VLANIDParameter().clean(10)
    10
    >>> VLANIDParameter().clean(5000)
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    >>> VLANIDParameter().clean(0)
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    """
    def __init__(self,required=True,default=None):
        super(VLANIDParameter,self).__init__(required=required,default=default,min_value=1,max_value=4095)
##
##
##
rx_mac_address_cisco=re.compile("^[0-9A-F]{4}\.[0-9A-F]{4}\.[0-9A-F]{4}$")
rx_mac_address_cisco_media=re.compile("^01[0-9A-F]{2}\.[0-9A-F]{4}\.[0-9A-F]{4}\.[0-9A-F]{2}$")
rx_mac_address_sixblock=re.compile("^([0-9A-F]{1,2}):([0-9A-F]{1,2}):([0-9A-F]{1,2}):([0-9A-F]{1,2}):([0-9A-F]{1,2}):([0-9A-F]{1,2})$")
class MACAddressParameter(StringParameter):
    """
    >>> MACAddressParameter().clean("1234.5678.9ABC")
    '12:34:56:78:9A:BC'
    >>> MACAddressParameter().clean("1234.5678.9abc")
    '12:34:56:78:9A:BC'
    >>> MACAddressParameter().clean("0112.3456.789a.bc")
    '12:34:56:78:9A:BC'
    >>> MACAddressParameter().clean("1234.5678.9abc.def0")
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    >>> MACAddressParameter().clean("12:34:56:78:9A:BC")
    '12:34:56:78:9A:BC'
    >>> MACAddressParameter().clean("12-34-56-78-9A-BC")
    '12:34:56:78:9A:BC'
    >>> MACAddressParameter().clean("0:13:46:50:87:5")
    '00:13:46:50:87:05'
    >>> MACAddressParameter().clean("12-34-56-78-9A-BC-DE")
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    >>> MACAddressParameter().clean("AB-CD-EF-GH-HJ-KL")
    Traceback (most recent call last):
        ...
    InterfaceTypeError
    """
    def clean(self,value):
        value=super(MACAddressParameter,self).clean(value)
        value=value.upper()
        match=rx_mac_address_cisco_media.match(value)
        if match:
            value=value.replace(".","")[2:]
            return "%s:%s:%s:%s:%s:%s"%(value[:2],value[2:4],value[4:6],value[6:8],value[8:10],value[10:])
        match=rx_mac_address_cisco.match(value)
        if match:
            value=value.replace(".","")
        else:
            value=value.replace("-",":")
            match=rx_mac_address_sixblock.match(value)
            if not match:
                raise InterfaceTypeError
            value=""
            for i in range(1,7):
                v=match.group(i)
                if len(v)==1:
                    v="0"+v
                value+=v
        return "%s:%s:%s:%s:%s:%s"%(value[:2],value[2:4],value[4:6],value[6:8],value[8:10],value[10:])
##
##
##
class Interface(object):
    def clean(self,**kwargs):
        in_kwargs=kwargs.copy()
        out_kwargs={}
        for n,p in [(n,p) for n,p in self.__class__.__dict__.items() if issubclass(p.__class__,Parameter)]:
            if n=="returns":
                continue
            if n not in in_kwargs and p.required:
                raise InterfaceTypeError("Parameter '%s' required"%n)
            if n in in_kwargs:
                try:
                    out_kwargs[n]=p.clean(in_kwargs[n])
                except InterfaceTypeError:
                    raise InterfaceTypeError("Invalid value for '%s'"%n)
                del in_kwargs[n]
        # Copy other parameters
        for k,v in in_kwargs.items():
            out_kwargs[k]=v
        return out_kwargs
    def clean_result(self,result):
        try:
            rp=self.returns
        except AttributeError:
            return result # No return result restriction
        return rp.clean(result)
    def requires_input(self):
        for n,p in [(n,p) for n,p in self.__class__.__dict__.items() if issubclass(p.__class__,Parameter)]:
            if n=="returns":
                continue
            return True
        return False
    def get_form(self,data=None):
        def get_clean_field_wrapper(form,name,param):
            def clean_field_wrapper(form,name,param):
                data=form.cleaned_data[name]
                if not param.required and not data:
                    return data
                try:
                    return param.form_clean(data)
                except InterfaceTypeError:
                    raise forms.ValidationError("Invalid value")
            return lambda: clean_field_wrapper(form,name,param)
        f=forms.Form(data)
        for n,p in [(n,p) for n,p in self.__class__.__dict__.items() if issubclass(p.__class__,Parameter)]:
            if n=="returns":
                continue
            f.fields[n]=p.get_form_field()
            setattr(f,"clean_%s"%n,get_clean_field_wrapper(f,n,p))
        return f
##
## Module Test
##
if __name__ == "__main__":
    import doctest
    doctest.testmod()
