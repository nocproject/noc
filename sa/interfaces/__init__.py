##
## Abstract script interfaces
##
import re,types

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
        
    def clean(self,value):
        raise InterfaceTypeError
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
        for k,v in in_value.items():
            out_value[k]=v
        return out_value
##
##
##
class IPParameter(StringParameter):
    def clean(self,value):
        v=super(IPParameter,self).clean(value)
        X=v.split(".")
        if len(X)!=4:
            raise InterfaceTypeError
        try:
            return len([x for x in X if 0<=int(x)<=255])==4
        except:
            return InterfaceTypeError
        return v
##
##
##
class Interface(object):
    def clean(self,**kwargs):
        in_kwargs=kwargs.copy()
        out_kwargs={}
        for n,p in [(n,p) for n,p in self.__class__.__dict__.items() if issubclass(p.__class__,Parameter)]:
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
##
## Module Test
##
if __name__ == "__main__":
    import doctest
    doctest.testmod()
