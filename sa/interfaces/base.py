# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Abstract script interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import datetime
# Third-party modules
import six
# NOC Modules
from noc.lib.text import list_to_ranges, ranges_to_list
from noc.core.ip import IPv6
from noc.core.mac import MAC
from noc.lib.validators import is_ipv6
from noc.core.interface.error import InterfaceTypeError
from noc.core.interface.parameter import BaseParameter as Parameter
from noc.core.interface.parameter import ORParameter  # noqa


class NoneParameter(Parameter):
    """
    >>> NoneParameter().clean(None)
    >>> NoneParameter().clean("None") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: NoneParameter: 'None'
    """
    def __init__(self, required=True):
        super(NoneParameter, self).__init__(required=required)

    def clean(self, value):
        if value is not None:
            self.raise_error(value)
        return value


class StringParameter(Parameter):
    """
    >>> StringParameter().clean("Test")
    'Test'
    >>> StringParameter().clean(10)
    '10'
    >>> StringParameter().clean(None)
    'None'
    >>> StringParameter(default="test").clean("no test")
    'no test'
    >>> StringParameter(default="test").clean(None)
    'test'
    >>> StringParameter(choices=["1","2"]).clean("1")
    '1'
    >>> StringParameter(choices=["1","2"]).clean("3") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: StringParameter: '3'.
    """
    def __init__(self, required=True, default=None, choices=None):
        self.choices = choices
        super(StringParameter, self).__init__(required=required,
                                              default=default)

    def clean(self, value):
        if not isinstance(value, str):
            if value is None and self.default is not None:
                return self.default
            try:
                value = str(value)
            except Exception:
                self.raise_error(value)
        if self.choices and value not in self.choices:
            self.raise_error(value)
        return value


class UnicodeParameter(StringParameter):
    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        try:
            value = unicode(value)
        except Exception:
            self.raise_error(value)
        if self.choices and value not in self.choices:
            self.raise_error(value)
        return value


class REStringParameter(StringParameter):
    """
    >>> REStringParameter("ex+p").clean("exp")
    'exp'
    >>> REStringParameter("ex+p").clean("exxp")
    'exxp'
    >>> REStringParameter("ex+p").clean("regexp 1")
    'regexp 1'
    >>> REStringParameter("ex+p").clean("ex") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: REStringParameter: 'ex'
    >>> REStringParameter("ex+p",default="exxp").clean("regexp 1")
    'regexp 1'
    >>> REStringParameter("ex+p",default="exxp").clean(None)
    'exxp'
    """
    def __init__(self, regexp, required=True, default=None):
        self.rx = re.compile(regexp)  # Compile before calling the constructor
        super(REStringParameter, self).__init__(required=required,
                                                default=default)

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        v = super(REStringParameter, self).clean(value)
        if not self.rx.search(v):
            self.raise_error(value)
        return v


class REParameter(StringParameter):
    """
    Check Regular Expression
    >>> REParameter().clean(".+?")
    '.+?'
    >>> REParameter().clean("+") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: REParameter: '+'
    """
    def clean(self, value):
        try:
            re.compile(value)
        except re.error:
            self.raise_error(value)
        return value


class PyExpParameter(StringParameter):
    """
    Check python expression
    >>> PyExpParameter().clean("(a + 3) * 7")
    '(a + 3) * 7'
    >>> PyExpParameter().clean("a =!= b") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: REParameter: 'a =!= b'
    """
    def clean(self, value):
        try:
            compile(value, "<string>", "eval")
        except SyntaxError:
            self.raise_error(value)
        return value


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
    >>> BooleanParameter().clean([]) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: BooleanParameter: [].
    >>> BooleanParameter(default=False).clean(None)
    False
    >>> BooleanParameter(default=True).clean(None)
    True
    """
    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        if isinstance(value, bool):
            return value
        if isinstance(value, six.integer_types):
            return value != 0
        if isinstance(value, six.string_types):
            return value.lower() in ("true", "t", "yes", "y")
        self.raise_error(value)

    def get_form_field(self, label=None):
        return {
            "xtype": "checkboxfield",
            "name": label,
            "boxLabel": label
        }


class IntParameter(Parameter):
    """
    >>> IntParameter().clean(1)
    1
    >>> IntParameter().clean("1")
    1
    >>> IntParameter().clean("not a number") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: IntParameter: 'not a number'
    >>> IntParameter(min_value=10).clean(5) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: IntParameter: 5
    >>> IntParameter(max_value=7).clean(10) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: IntParameter: 10
    >>> IntParameter(max_value=10, default=7).clean(5)
    5
    >>> IntParameter(max_value=10, default=7).clean(None)
    7
    >>> IntParameter(max_value=10, default=15) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: IntParameter: 15
    >>> IntParameter().clean(None) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: IntParameter: None
    None
    """
    def __init__(self, required=True, default=None,
                 min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        super(IntParameter, self).__init__(required=required, default=default)

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        try:
            i = int(value)
        except (ValueError, TypeError):
            self.raise_error(value)
        if ((self.min_value is not None and i < self.min_value) or
                (self.max_value is not None and i > self.max_value)):
            self.raise_error(value)
        return i


class FloatParameter(Parameter):
    """
    >>> FloatParameter().clean(1.2)
    1.2
    >>> FloatParameter().clean("1.2")
    1.2
    >>> FloatParameter().clean("not a number") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: FloatParameter: 'not a number'
    >>> FloatParameter(min_value=10).clean(5) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: FloatParameter: 5
    >>> FloatParameter(max_value=7).clean(10) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: FloatParameter: 10
    >>> FloatParameter(max_value=10,default=7).clean(5)
    5.0
    >>> FloatParameter(max_value=10,default=7).clean(None)
    7.0
    >>> FloatParameter(max_value=10,default=15) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: FloatParameter: 15
    """
    def __init__(self, required=True, default=None,
                 min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        super(FloatParameter, self).__init__(required=required, default=default)

    def clean(self, value):
        if not isinstance(value, float):
            if value is None and self.default is not None:
                return self.default
            try:
                value = float(value)
            except ValueError:
                self.raise_error(value)
        if ((self.min_value is not None and value < self.min_value) or
                (self.max_value is not None and value > self.max_value)):
            self.raise_error(value)
        return value


class ListParameter(Parameter):
    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        try:
            return list(value)
        except ValueError:
            self.raise_error(value)

    def form_clean(self, value):
        try:
            return self.clean(eval(value, {}, {}))
        except Exception:
            self.raise_error(value)


class InstanceOfParameter(Parameter):
    """
    >>> class C: pass
    >>> class X: pass
    >>> class CC(C): pass
    >>> InstanceOfParameter(cls=C).clean(C()) and "Ok"
    'Ok'
    >>> InstanceOfParameter(cls=C).clean(CC()) and "Ok"
    'Ok'
    >>> InstanceOfParameter(cls=C).clean(1) and "Ok" #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: InstanceOfParameter: 1
    >>> InstanceOfParameter(cls="C").clean(C()) and "Ok"
    'Ok'
    >>> InstanceOfParameter(cls="C").clean(1) and "Ok" #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: InstanceOfParameter: 1
    """
    def __init__(self, cls, required=True, default=None):
        super(InstanceOfParameter, self).__init__(required=required,
                                                  default=default)
        self.cls = cls
        if isinstance(cls, basestring):
            self.is_valid = self.is_valid_classname
        else:
            self.is_valid = self.is_valid_instance

    def is_valid_instance(self, value):
        return isinstance(value, self.cls)

    def is_valid_classname(self, value):
        return (hasattr(value, "__class__") and
                value.__class__.__name__ == self.cls)

    def clean(self, value):
        if value is None:
            if self.default is not None:
                return self.default
            if not self.required:
                return None
        try:
            if self.is_valid(value):
                return value
        except Exception:
            pass
        self.raise_error(value)


class SubclassOfParameter(Parameter):
    """
    >>> class C: pass
    >>> class C1(C): pass
    >>> class C2(C1): pass
    >>> class C3(C1): pass
    >>> SubclassOfParameter(cls=C).clean(C2) and "Ok"
    'Ok'
    >>> SubclassOfParameter(cls=C).clean(1) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: SubclassOfParameter: 1
    >>> SubclassOfParameter(cls="C").clean(C2) and "Ok"
    'Ok'
    >>> SubclassOfParameter(cls=C).clean(1) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: SubclassOfParameter: 1
    >>> SubclassOfParameter(cls=C2).clean(C3) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: SubclassOfParameter: <class base.C3>
    >>> SubclassOfParameter(cls="C",required=False).clean(None)
    """
    def __init__(self, cls, required=True, default=None):
        super(SubclassOfParameter, self).__init__(required=required,
                                                  default=default)
        self.cls = cls
        if isinstance(cls, basestring):
            self.is_valid = self.is_valid_classname
        else:
            self.is_valid = self.is_valid_class

    def is_valid_classname(self, value):
        def check_name(c, name):
            # Check class name
            if c.__name__ == name:
                return True
            # Check base classes name
            for bc in c.__bases__:
                if check_name(bc, name):
                    return True
            #
            return False

        return check_name(value, self.cls)

    def is_valid_class(self, value):
        return issubclass(value, self.cls)

    def clean(self, value):
        if value is None:
            if self.default is not None:
                return self.default
            if not self.required:
                return None
        try:
            if self.is_valid(value):
                return value
        except Exception:
            pass
        self.raise_error(value)


class ListOfParameter(ListParameter):
    """
    >>> ListOfParameter(element=IntParameter()).clean([1,2,3])
    [1, 2, 3]
    >>> ListOfParameter(element=IntParameter()).clean([1,2,"3"])
    [1, 2, 3]
    >>> ListOfParameter(element=IntParameter()).clean([1,2,"x"]) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: IntParameter: 'x'
    >>> ListOfParameter(element=StringParameter()).clean([1,2,3,"x"])
    ['1', '2', '3', 'x']
    >>> ListOfParameter(element=StringParameter(),default=[]).clean(None)
    []
    >>> ListOfParameter(element=StringParameter(),default=[1,2,3]).clean(None)
    ['1', '2', '3']
    >>> ListOfParameter(element=[StringParameter(), IntParameter()]).clean([("a",1), ("b", "2")])
    [['a', 1], ['b', 2]]
    >>> ListOfParameter(element=[StringParameter(), IntParameter()]).clean([("a",1), ("b", "x")])   #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: IntParameter: 'x'
    """
    def __init__(self, element, required=True, default=None, convert=False):
        self.element = element
        self.is_list = type(element) in (list, tuple)
        self.convert = convert
        super(ListOfParameter, self).__init__(required=required,
                                              default=default)

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        if self.convert and not isinstance(value, (list, tuple)):
            value = [value]
        v = super(ListOfParameter, self).clean(value)
        if self.is_list:
            return [
                [e.clean(vv) for e, vv in zip(self.element, nv)]
                for nv in value
            ]
        else:
            return [self.element.clean(x) for x in v]

    def script_clean_input(self, profile, value):
        if value is None and self.default is not None:
            return self.default
        v = super(ListOfParameter, self).script_clean_input(profile, value)
        if self.is_list:
            return [
                [e.script_clean_input(profile, vv) for e, vv in zip(self.element, nv)]
                for nv in value
            ]
        else:
            return [self.element.script_clean_input(profile, x) for x in v]

    def script_clean_result(self, profile, value):
        if value is None and self.default is not None:
            return self.default
        v = super(ListOfParameter, self).script_clean_result(profile, value)
        if self.is_list:
            return [
                [e.script_clean_result(profile, vv) for e, vv in zip(self.element, nv)]
                for nv in value
            ]
        else:
            return [
                self.element.script_clean_result(profile, x)
                for x in v
            ]


class StringListParameter(ListOfParameter):
    """
    >>> StringListParameter().clean(["1","2","3"])
    ['1', '2', '3']
    >>> StringListParameter().clean(["1",2,"3"])
    ['1', '2', '3']
    """
    def __init__(self, required=True, default=None, convert=False):
        super(StringListParameter, self).__init__(
            element=StringParameter(), required=required,
            default=default, convert=convert)


class DictParameter(Parameter):
    """
    >>> DictParameter(attrs={"i":IntParameter(),"s":StringParameter()}).clean({"i":10,"s":"ten"})
    {'i': 10, 's': 'ten'}
    >>> DictParameter(attrs={"i":IntParameter(),"s":StringParameter()}).clean({"i":"10","x":"ten"}) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: DictParameter: {'i': '10', 'x': 'ten'}
    """
    def __init__(self, required=True, default=None, attrs=None, truncate=False):
        super(DictParameter, self).__init__(required=required, default=default)
        self.attrs = attrs or {}
        self.truncate = truncate
        self._defaults = dict(
            (k, attrs[k].default)
            for k in self.attrs
            if self.attrs[k].default is not None
        )
        self._required_input = set(k for k in self.attrs if self.attrs[k].required)

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        if not isinstance(value, dict):
            self.raise_error(value)
        if not self.attrs:
            return value
        out = self._defaults.copy()
        for k in value:
            param = self.attrs.get(k)
            if param:
                v = value[k]
                if v is None:
                    continue
                try:
                    out[k] = param.clean(v)
                except InterfaceTypeError as e:
                    self.raise_error("Invalid value for '%s': %s" % (k, e))
            elif not self.truncate:
                out[k] = value[k]
        missed = self._required_input - set(out)
        if missed:
            raise InterfaceTypeError("Parameter '%s' required" % missed.pop())
        return out

    def script_clean_input(self, profile, value):
        if value is None and self.default is not None:
            return self.default
        if not isinstance(value, dict):
            self.raise_error(value)
        if not self.attrs:
            return value
        in_value = value.copy()
        out_value = {}
        for a_name, attr in self.attrs.items():
            if a_name not in in_value and attr.required:
                self.raise_error(value, "Attribute '%s' required" % a_name)
            if a_name in in_value:
                try:
                    out_value[a_name] = attr.script_clean_input(profile, in_value[a_name])
                except InterfaceTypeError:
                    self.raise_error(value, "Invalid value for '%s'" % a_name)
                del in_value[a_name]
        for k, v in in_value.items():
            out_value[k] = v
        return out_value

    def script_clean_result(self, profile, value):
        if value is None and self.default is not None:
            return self.default
        if not isinstance(value, dict):
            self.raise_error(value)
        if not self.attrs:
            return value
        in_value = value.copy()
        out_value = {}
        for a_name, attr in self.attrs.items():
            if a_name not in in_value and attr.required:
                self.raise_error(value, "Attribute '%s' required" % a_name)
            if a_name in in_value:
                try:
                    out_value[a_name] = attr.script_clean_result(profile, in_value[a_name])
                except InterfaceTypeError:
                    self.raise_error(value, "Invalid value for '%s'" % a_name)
                del in_value[a_name]
        for k, v in in_value.items():
            out_value[k] = v
        return out_value


class DictListParameter(ListOfParameter):
    """
    >>> DictListParameter().clean([{"1": 2},{"2":3, "4":1}])
    [{'1': 2}, {'2': 3, '4': 1}]
    >>> DictListParameter(attrs={"i":IntParameter(),"s":StringParameter()}).clean([{"i":10,"s":"ten"},{"i":"5","s":"five"}])
    [{'i': 10, 's': 'ten'}, {'i': 5, 's': 'five'}]
    >>> DictListParameter(attrs={"i":IntParameter(),"s":StringParameter()},convert=True).clean({"i":"10","s":"ten"})
    [{'i': 10, 's': 'ten'}]
    """
    def __init__(self, required=True, default=None,
                 attrs=None, convert=False):
        super(DictListParameter, self).__init__(
            element=DictParameter(attrs=attrs),
            required=required, default=default, convert=convert)


class DateTimeParameter(StringParameter):
    rx_datetime = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$")

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        if value.lower() == "infinite":
            return datetime.datetime(year=datetime.MAXYEAR, month=1, day=1)
        if self.rx_datetime.match(value):
            return value
        self.raise_error(value)

    def form_clean(self, value):
        if value is None and self.default is not None:
            value = self.default
        if isinstance(value, basestring):
            if "." in value:
                dt, _, us = value.partition(".")
                dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
                us = int(us.rstrip("Z"), 10)
                return dt + datetime.timedelta(microseconds=us)
            else:
                return datetime.datetime.strptime(value,
                                                  "%Y-%m-%dT%H:%M:%S")
        elif isinstance(value, datetime):
            return value
        else:
            self.raise_error(value)


class DateTimeShiftParameter(StringParameter):
    rx_datetime = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(\+\d{4})?$")

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        if value.lower() == "infinite":
            return datetime.datetime(year=datetime.MAXYEAR, month=1, day=1)
        if self.rx_datetime.match(value):
            return value
        self.raise_error(value)

    def form_clean(self, value):
        if value is None and self.default is not None:
            value = self.default
        if isinstance(value, basestring):
            if "." in value:
                dt, _, us = value.partition(".")
                dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
                if "+" in us:
                    us, offset = us.split("+")
                us = int(us.rstrip("Z"), 10)
                return dt + datetime.timedelta(microseconds=us)
            else:
                return datetime.datetime.strptime(value,
                                                  "%Y-%m-%dT%H:%M:%S")
        elif isinstance(value, datetime):
            return value
        else:
            self.raise_error(value)


class IPv4Parameter(StringParameter):
    """
    >>> IPv4Parameter().clean("192.168.0.1")
    '192.168.0.1'
    >>> IPv4Parameter().clean("192.168.0.256") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: IPvParameter: '192.168.0.256'
    """
    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        try:
            int(value)
            return value
        except ValueError:
            pass
        if len(value) == 4:
            # IP address in binary form
            value = ".".join(["%02X" % ord(c) for c in value])
        v = super(IPv4Parameter, self).clean(value)
        X = v.split(".")
        if len(X) != 4:
            self.raise_error(value)
        try:
            if len([x for x in X if 0 <= int(x) <= 255]) != 4:
                self.raise_error(value)
        except ValueError:
            self.raise_error(value)
        # Avoid output like 001.002.003.004
        v = ".".join("%d" % int(c) for c in X)
        return v


class IPv4PrefixParameter(StringParameter):
    """
    >>> IPv4PrefixParameter().clean("192.168.0.0/16")
    '192.168.0.0/16'
    >>> IPv4PrefixParameter().clean("192.168.0.256") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: IPv4PrefixParameter: '192.168.0.256'
    >>> IPv4PrefixParameter().clean("192.168.0.0/33") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: IPv4PrefixParameter: '192.168.0.0/33'
    >>> IPv4PrefixParameter().clean("192.168.0.0/-5") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: IPv4PrefixParameter: '192.168.0.0/-5'
    """
    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        v = super(IPv4PrefixParameter, self).clean(value)
        if "/" not in v:
            self.raise_error(value)
        n, m = v.split("/", 1)
        try:
            m = int(m)
        except ValueError:
            self.raise_error(value)
        if m < 0 or m > 32:
            self.raise_error(value)
        X = n.split(".")
        if len(X) != 4:
            self.raise_error(value)
        try:
            if len([x for x in X if 0 <= int(x) <= 255]) != 4:
                self.raise_error(value)
        except ValueError:
            self.raise_error(value)
        return v


#
# IPv6 Parameter
#
class IPv6Parameter(StringParameter):
    """
    >>> IPv6Parameter().clean("::")
    '::'
    >>> IPv6Parameter().clean("::1")
    '::1'
    >>> IPv6Parameter().clean("2001:db8::1")
    '2001:db8::1'
    >>> IPv6Parameter().clean("2001:db8::")
    '2001:db8::'
    >>> IPv6Parameter().clean("::ffff:192.168.0.1")
    '::ffff:192.168.0.1'
    >>> IPv6Parameter().clean('g::')  #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: IPv6Parameter: 'g::'.
    >>> IPv6Parameter().clean("0:00:0:0:0::1")
    '::1'
    >>> IPv6Parameter().clean("::ffff:c0a8:1")
    '::ffff:192.168.0.1'
    >>> IPv6Parameter().clean("2001:db8:0:7:0:0:0:1")
    '2001:db8:0:7::1'
    """
    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        v = super(IPv6Parameter, self).clean(value)
        if not is_ipv6(v):
            self.raise_error(value)
        return IPv6(v).normalized.address


class IPv6PrefixParameter(StringParameter):
    """
    >>> IPv6PrefixParameter().clean("::/128")
    '::/128'
    >>> IPv6PrefixParameter().clean("2001:db8::/32")
    '2001:db8::/32'
    >>> IPv6PrefixParameter().clean("2001:db8::/129") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: IPv6PrefixParameter: '2001:db8::/129'
    >>> IPv6PrefixParameter().clean("2001:db8::/g") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: IPv6PrefixParameter: '2001:db8::/g'
    >>> IPv6PrefixParameter().clean("2001:db8::") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: IPv6PrefixParameter: '2001:db8::'
    """
    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        v = super(IPv6PrefixParameter, self).clean(value)
        if "/" not in v:
            self.raise_error(value)
        n, m = v.split("/", 1)
        try:
            m = int(m)
        except ValueError:
            self.raise_error(value)
        if m < 0 or m > 128:
            self.raise_error(value)
        n = IPv6Parameter().clean(n)
        return "%s/%d" % (n, m)


#
# IPv4/IPv6 parameter
#
class IPParameter(StringParameter):
    def clean(self, value):
        """
        >>> IPParameter().clean("192.168.0.1")
        '192.168.0.1'
        >>> PrefixParameter().clean("2001:db8::/32")
        '2001:db8::/32'
        """
        if ":" in value:
            return IPv6Parameter().clean(value)
        else:
            return IPv4Parameter().clean(value)


#
# Prefix parameter
#
class PrefixParameter(StringParameter):
    def clean(self, value):
        """
        >>> PrefixParameter().clean("192.168.0.0/24")
        '192.168.0.0/24'
        """
        if ":" in value:
            return IPv6PrefixParameter().clean(value)
        else:
            return IPv4PrefixParameter().clean(value)


#
#
#
class VLANIDParameter(IntParameter):
    """
    >>> VLANIDParameter().clean(10)
    10
    >>> VLANIDParameter().clean(5000) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: VLANIDParameter: 5000
    >>> VLANIDParameter().clean(0) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: VLANIDParameter: 0
    """
    def __init__(self, required=True, default=None):
        super(VLANIDParameter, self).__init__(required=required, default=default,
                                              min_value=1, max_value=4095)


class VLANStackParameter(ListOfParameter):
    """
    >>> VLANStackParameter().clean(10)
    [10]
    >>> VLANStackParameter().clean([10])
    [10]
    >>> VLANStackParameter().clean([10, "20"])
    [10, 20]
    >>> VLANStackParameter().clean([10, 0])
    [10, 0]
    """

    def __init__(self, required=True, default=None):
        super(VLANStackParameter, self).__init__(
            element=IntParameter(),
            required=required,
            default=default, convert=True
        )

    def clean(self, value):
        value = super(VLANStackParameter, self).clean(value)
        if len(value) > 0:
            value[0] = VLANIDParameter().clean(value[0])
        for i in range(1, len(value)):
            value[i] = IntParameter(min_value=0, max_value=4095).clean(value[i])
        return value


#
#
#
class VLANIDListParameter(ListOfParameter):
    """
    >>> VLANIDListParameter().clean(["1","2","3"])
    [1, 2, 3]
    >>> VLANIDListParameter().clean([1,2,3])
    [1, 2, 3]
    """
    def __init__(self, required=True, default=None):
        super(VLANIDListParameter, self).__init__(
            element=VLANIDParameter(),
            required=required, default=default
        )


class VLANIDMapParameter(StringParameter):
    def clean(self, value):
        """
        >>> VLANIDMapParameter().clean("1,2,5-10")
        '1-2,5-10'
        >>> VLANIDMapParameter().clean("")
        ''
        """
        if isinstance(value, basestring) and not value.strip():
            return ""
        vp = VLANIDParameter()
        try:
            return list_to_ranges([vp.clean(v) for v in ranges_to_list(value)])
        except SyntaxError:
            self.raise_error(value)


class MACAddressParameter(StringParameter):
    """
    >>> MACAddressParameter().clean("1234.5678.9ABC")
    '12:34:56:78:9A:BC'
    >>> MACAddressParameter().clean("1234.5678.9abc")
    '12:34:56:78:9A:BC'
    >>> MACAddressParameter().clean("0112.3456.789a.bc")
    '12:34:56:78:9A:BC'
    >>> MACAddressParameter().clean("1234.5678.9abc.def0") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: MACAddressParameter: '1234.5678.9ABC.DEF0'
    >>> MACAddressParameter().clean("12:34:56:78:9A:BC")
    '12:34:56:78:9A:BC'
    >>> MACAddressParameter().clean("12-34-56-78-9A-BC")
    '12:34:56:78:9A:BC'
    >>> MACAddressParameter().clean("0:13:46:50:87:5")
    '00:13:46:50:87:05'
    >>> MACAddressParameter().clean("123456-789abc")
    '12:34:56:78:9A:BC'
    >>> MACAddressParameter().clean("12-34-56-78-9A-BC-DE") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: MACAddressParameter: '12:34:56:78:9A:BC:DE'
    >>> MACAddressParameter().clean("AB-CD-EF-GH-HJ-KL") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: MACAddressParameter: 'AB:CD:EF:GH:HJ:KL'
    >>> MACAddressParameter().clean("aabb-ccdd-eeff")
    'AA:BB:CC:DD:EE:FF'
    >>> MACAddressParameter().clean("aabbccddeeff")
    'AA:BB:CC:DD:EE:FF'
    >>> MACAddressParameter().clean("AABBCCDDEEFF")
    'AA:BB:CC:DD:EE:FF'
    >>> MACAddressParameter().clean("\\xa8\\xf9K\\x80\\xb4\\xc0")
    'A8:F9:4B:80:B4:C0'
    >>> MACAddressParameter(accept_bin=False).clean("\\xa8\\xf9K\\x80\\xb4\\xc0") #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: MACAddressParameter: '\xa8\xf9K\x80\xb4\xc0'.
    """
    def __init__(self, required=True, default=None, accept_bin=True):
        self.accept_bin = accept_bin
        super(MACAddressParameter, self).__init__(required=required,
                                                  default=default)

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        if isinstance(value, six.string_types):
            value = super(MACAddressParameter, self).clean(value)
        if not self.accept_bin and len(value) <= 6:
            self.raise_error(value)
        try:
            return str(MAC(value))
        except ValueError:
            self.raise_error(value)


class InterfaceNameParameter(StringParameter):
    def script_clean_input(self, profile, value):
        return profile.convert_interface_name(value)

    def script_clean_result(self, profile, value):
        return self.script_clean_input(profile, value)


class OIDParameter(Parameter):
    """
    >>> OIDParameter().clean("1.3.6.1.2.1.1.1.0")
    '1.3.6.1.2.1.1.1.0'
    >>> OIDParameter(default="1.3.6.1.2.1.1.1.0").clean(None)
    '1.3.6.1.2.1.1.1.0'
    >>> OIDParameter().clean("1.3.6.1.2.1.1.X.0")  #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: OIDParameter: '1.3.6.1.2.1.1.X.0'
    """
    def clean(self, value):
        def is_false(v):
            try:
                v = int(v)
            except ValueError:
                return True
            return v < 0

        if value is None and self.default is not None:
            return self.default
        if bool([v for v in value.split(".") if is_false(v)]):
            self.raise_error(value)
        return value


class RDParameter(Parameter):
    def clean(self, value):
        """
        >>> RDParameter().clean("100:4294967295")
        '100:4294967295'
        >>> RDParameter().clean("10.10.10.10:10")
        '10.10.10.10:10'
        >>> RDParameter().clean("100000:500")
        '100000:500'
        >>> RDParameter().clean("100000L:100")
        '100000:100'
        """
        try:
            left, right = value.split(":", 1)
            right = long(right)
        except ValueError:
            self.raise_error(value)
        if right < 0:
            self.raise_error(value)
        if "." in left:
            # IP:N
            try:
                left = IPv4Parameter().clean(left)
            except InterfaceTypeError:
                self.raise_error(value)
            if right > 65535:
                self.raise_error(value)
        else:
            # ASN:N
            try:
                if left.endswith("L") or left.endswith("l"):
                    left = left[:-1]
                left = int(left)
            except ValueError:
                self.raise_error(value)
            if left < 0:
                self.raise_error(value)
            if left > 65535:
                if right > 65535:  # 4-byte ASN
                    self.raise_error(value)
            else:
                if right > 0xFFFFFFFF:  # 2-byte ASN
                    self.raise_error(value)
        return "%s:%s" % (left, right)


class GeoPointParameter(Parameter):
    """
    >>> GeoPointParameter().clean([180, 90])
    [180.0, 90.0]
    >>> GeoPointParameter().clean([75.5, "90"])
    [75.5, 90.0]
    >>> GeoPointParameter().clean("[180, 85.5]")
    [180.0, 85.5]
    >>> GeoPointParameter().clean([1])  #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    ValueError: GeoPointParameter: [1]
    """
    def clean(self, value):
        if type(value) in (list, tuple):
            # List or tuple
            if len(value) != 2:
                self.raise_error(value)
            try:
                return [float(x) for x in value]
            except ValueError:
                self.raise_error(value)
        elif isinstance(value, basestring):
            v = value.replace(" ", "")
            if not v or "," not in v:
                self.raise_error(value)
            s = v[0]
            if s not in ("(", "[") or (s == "(" and v[-1] != ")") or (s == "[" and v[-1]) != "]":
                self.raise_error(value)
            return self.clean(v[1:-1].split(","))
        else:
            self.raise_error(value)


class ModelParameter(Parameter):
    """
    Model reference parameter
    """
    def __init__(self, model, required=True):
        super(ModelParameter, self).__init__(required=required)
        self.model = model

    def clean(self, value):
        if not value:
            if self.required:
                self.raise_error("Value required")
            else:
                return None
        try:
            value = int(value)
        except ValueError:
            self.raise_error(value)
        try:
            return self.model.objects.get(pk=value)
        except self.model.DoesNotExist:
            self.raise_error("Not found: %d" % value)


DocFieldMap = {
    "FloatField": FloatParameter()
}


class DocumentParameter(Parameter):
    """
    Document reference parameter
    """
    def __init__(self, document, required=True):
        super(DocumentParameter, self).__init__(required=required)
        self.document = document
        self.has_get_by_id = bool(getattr(self.document, "get_by_id", None))

    def clean(self, value):
        if not value:
            if self.required:
                self.raise_error("Value required")
            else:
                return None
        if self.has_get_by_id:
            v = self.document.get_by_id(value)
        else:
            v = self.document.objects.filter(id=value).first()
        if not v:
            self.raise_error("Not found: %d" % value)
        return v


class EmbeddedDocumentParameter(Parameter):
    def __init__(self, document, required=True):
        super(EmbeddedDocumentParameter, self).__init__(
            required=required)
        self.document = document

    def clean(self, value):
        if not value:
            if self.required:
                self.raise_error("Value required")
            else:
                return None
        if not isinstance(value, dict):
            self.raise_error(value, "Value must be list dict")
        for k, v in self.document._fields.iteritems():
            if k in value and value[k] is not None:
                p = DocFieldMap.get(v.__class__.__name__)
                if p:
                    value[k] = p.clean(value[k])
        return self.document(**value)


class TagsParameter(Parameter):
    """
    >>> TagsParameter().clean([1, 2, "tags"])
    [u'1', u'2', u'tags']
    >>> TagsParameter().clean([1, 2, "tags "])
    [u'1', u'2', u'tags']
    >>> TagsParameter().clean("1,2,tags")
    [u'1', u'2', u'tags']
    >>> TagsParameter().clean("1 , 2,  tags")
    [u'1', u'2', u'tags']
    """
    def clean(self, value):
        if type(value) in (list, tuple):
            v = [unicode(v).strip() for v in value]
            return [x for x in v if x]
        elif isinstance(value, basestring):
            v = [unicode(x.strip()) for x in value.split(",")]
            return [x for x in v if x]
        else:
            self.raise_error("Invalid tags: %s" % value)


class ColorParameter(Parameter):
    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        if type(value) in (int, long):
            return value
        if isinstance(value, basestring):
            if value.startswith("#"):
                value = value[1:]
            if len(value) == 6:
                try:
                    return int(value, 16)
                except ValueError:
                    self.raise_error(value)
        self.raise_error(value)


class ObjectIdParameter(REStringParameter):
    def __init__(self, required=True, default=None):
        super(ObjectIdParameter, self).__init__(
            "^[0-9a-f]{24}$", required=required, default=default
        )


if __name__ == "__main__":
    import doctest
    doctest.testmod()
