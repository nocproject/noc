# ----------------------------------------------------------------------
# Abstract script interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
import datetime

# NOC Modules
from noc.core.text import list_to_ranges, ranges_to_list
from noc.core.ip import IPv6
from noc.core.mac import MAC
from noc.core.validators import is_ipv6
from noc.core.interface.error import InterfaceTypeError
from noc.core.interface.parameter import BaseParameter as Parameter
from noc.core.interface.parameter import ORParameter  # noqa
from noc.core.discriminator import discriminator
from noc.core.comp import smart_text


class NoneParameter(Parameter):
    """
    Checks value is None
    """

    def __init__(self, required=True):
        super().__init__(required=required)

    def clean(self, value):
        if value is not None:
            self.raise_error(value)
        return value


class StringParameter(Parameter):
    """
    Check value is string
    """

    def __init__(self, required=True, default=None, choices=None, aliases=None, strip_value=False):
        self.choices = set(choices) if choices else None
        self.aliases = aliases
        self.strip_value = strip_value
        super().__init__(required=required, default=default)

    def clean(self, value):
        if not isinstance(value, str):
            if value is None and self.default is not None:
                return self.default
            try:
                value = str(value)
            except Exception:
                self.raise_error(value)
        if self.strip_value:
            value = value.strip()
        if self.aliases:
            value = self.aliases.get(value, value)
        if self.choices and value not in self.choices:
            self.raise_error(value)
        return value


class UnicodeParameter(StringParameter):
    """
    Check value is unicode
    """

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        try:
            value = smart_text(value)
        except Exception:
            self.raise_error(value)
        if self.choices and value not in self.choices:
            self.raise_error(value)
        return value


class REStringParameter(StringParameter):
    """
    Check value is string matching regular expression
    """

    def __init__(self, regexp, required=True, default=None):
        self.rx = re.compile(regexp)  # Compile before calling the constructor
        super().__init__(required=required, default=default)

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        v = super().clean(value)
        if not self.rx.search(v):
            self.raise_error(value)
        return v


class REParameter(StringParameter):
    """
    Check value is valid regular expression
    """

    def clean(self, value):
        try:
            re.compile(value)
        except re.error:
            self.raise_error(value)
        return value


class PyExpParameter(StringParameter):
    """
    Check value is valid python expression
    """

    def clean(self, value):
        try:
            compile(value, "<string>", "eval")
        except SyntaxError:
            self.raise_error(value)
        return value


class BooleanParameter(Parameter):
    """
    Check value is boolean
    """

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value != 0
        if isinstance(value, str):
            return value.lower() in ("true", "t", "yes", "y")
        self.raise_error(value)

    def get_form_field(self, label=None):
        return {"xtype": "checkboxfield", "name": label, "boxLabel": label}


class IntParameter(Parameter):
    """
    Check value is integer
    """

    def __init__(self, required=True, default=None, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(required=required, default=default)

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        try:
            i = int(value)
        except (ValueError, TypeError):
            self.raise_error(value)
        if (self.min_value is not None and i < self.min_value) or (
            self.max_value is not None and i > self.max_value
        ):
            self.raise_error(value)
        return i


class FloatParameter(Parameter):
    """
    Check value is float
    """

    def __init__(self, required=True, default=None, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(required=required, default=default)

    def clean(self, value):
        if not isinstance(value, float):
            if value is None and self.default is not None:
                return self.default
            try:
                value = float(value)
            except ValueError:
                self.raise_error(value)
        if (self.min_value is not None and value < self.min_value) or (
            self.max_value is not None and value > self.max_value
        ):
            self.raise_error(value)
        return value


class ListParameter(Parameter):
    """
    Check value is list
    """

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
    Check value is an instance of class
    """

    def __init__(self, cls, required=True, default=None):
        super().__init__(required=required, default=default)
        self.cls = cls
        if isinstance(cls, str):
            self.is_valid = self.is_valid_classname
        else:
            self.is_valid = self.is_valid_instance

    def is_valid_instance(self, value):
        return isinstance(value, self.cls)

    def is_valid_classname(self, value):
        return hasattr(value, "__class__") and value.__class__.__name__ == self.cls

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
    Check value is subclass of given class
    """

    def __init__(self, cls, required=True, default=None):
        super().__init__(required=required, default=default)
        self.cls = cls
        if isinstance(cls, str):
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
    Check value is a list of given parameter type
    """

    def __init__(self, element, required=True, default=None, convert=False):
        self.element = element
        self.is_list = isinstance(element, (list, tuple))
        self.convert = convert
        super().__init__(required=required, default=default)

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        if self.convert and not isinstance(value, (list, tuple)):
            value = [value]
        v = super().clean(value)
        if self.is_list:
            return [[e.clean(vv) for e, vv in zip(self.element, nv)] for nv in value]
        else:
            return [self.element.clean(x) for x in v]

    def script_clean_input(self, profile, value):
        if value is None and self.default is not None:
            return self.default
        v = super().script_clean_input(profile, value)
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
        v = super().script_clean_result(profile, value)
        if self.is_list:
            return [
                [e.script_clean_result(profile, vv) for e, vv in zip(self.element, nv)]
                for nv in value
            ]
        else:
            return [self.element.script_clean_result(profile, x) for x in v]


class StringListParameter(ListOfParameter):
    """
    Check value is list of strings
    """

    def __init__(self, required=True, default=None, convert=False, choices=None, strict=False):
        self.strict = strict
        super().__init__(
            element=StringParameter(choices=choices),
            required=required,
            default=default,
            convert=convert,
        )

    def clean(self, value):
        if self.strict and isinstance(value, str):
            raise InterfaceTypeError("Must be List")
        return super().clean(value)


class LabelParameter(Parameter):
    """
    Check value is string
    """

    def __init__(
        self,
        required=True,
        default=None,
        choices=None,
        aliases=None,
        default_scope=None,
        allowed_scopes=None,
    ):
        self.choices = set(choices) if choices else None
        self.aliases = aliases
        self.default_scope = default_scope
        self.allowed_scopes = allowed_scopes or set()
        super().__init__(required=required, default=default)

    def clean(self, value):
        if not isinstance(value, str):
            if value is None and self.default is not None:
                return self.default
            try:
                value = str(value)
            except Exception:
                self.raise_error(value)
        if self.aliases:
            value = self.aliases.get(value, value)
        if self.choices and value not in self.choices:
            self.raise_error(value)
        s, *v = value.rsplit("::", 1)
        if not v and not self.default_scope:
            self.raise_error(value, msg="Label without scope is not allowed")
        elif not v:
            value = f"{self.default_scope}::{value}"
        if self.allowed_scopes and s not in self.allowed_scopes:
            self.raise_error(value, msg=f"Not allowed scope: {s}")
        return value


class LabelListParameter(ListOfParameter):
    """ """

    def __init__(
        self,
        required=True,
        default=None,
        convert=False,
        choices=None,
        default_scope=None,
        allowed_scopes=None,
    ):
        super().__init__(
            element=LabelParameter(
                choices=choices, default_scope=default_scope, allowed_scopes=allowed_scopes
            ),
            required=required,
            default=default,
            convert=convert,
        )


class DictParameter(Parameter):
    """
    Check value is a dict
    """

    def __init__(self, required=True, default=None, attrs=None, truncate=False):
        super().__init__(required=required, default=default)
        self.attrs = attrs or {}
        self.truncate = truncate
        self._defaults = {
            k: attrs[k].default for k in self.attrs if self.attrs[k].default is not None
        }
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
    Check value is a list of dicts of given structure
    """

    def __init__(self, required=True, default=None, attrs=None, convert=False):
        super().__init__(
            element=DictParameter(attrs=attrs), required=required, default=default, convert=convert
        )


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
        if isinstance(value, str):
            if "." in value:
                dt, _, us = value.partition(".")
                dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
                us = int(us.rstrip("Z"), 10)
                return dt + datetime.timedelta(microseconds=us)
            else:
                return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
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
        if isinstance(value, str):
            if "." in value:
                dt, _, us = value.partition(".")
                dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
                if "+" in us:
                    us, offset = us.split("+")
                us = int(us.rstrip("Z"), 10)
                return dt + datetime.timedelta(microseconds=us)
            else:
                return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        elif isinstance(value, datetime):
            return value
        else:
            self.raise_error(value)


class IPv4Parameter(StringParameter):
    """
    Check value is IPv4 address
    """

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        try:
            int(value)
            return value
        except ValueError:
            pass
        if len(value) == 4 and isinstance(value, bytes):
            value = ".".join(str(c) for c in value)
        elif len(value) == 4:
            # IP address in binary form
            value = ".".join(["%02X" % ord(c) for c in value])
        v = super().clean(value)
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
    Check value is IPv4 prefix
    """

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        v = super().clean(value)
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


class IPv6Parameter(StringParameter):
    """
    Check value is IPv6 address
    """

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        if len(value) == 16 and isinstance(value, bytes):
            value = ":".join("%02X%02X" % (x, y) for x, y in zip(value[0::2], value[1::2]))
        v = super().clean(value)
        if not is_ipv6(v):
            self.raise_error(value)
        return IPv6(v).normalized.address


class IPv6PrefixParameter(StringParameter):
    """
    Check value is IPv6 prefix
    """

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        v = super().clean(value)
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


class IPParameter(StringParameter):
    """
    Check value is IPv4 or IPv6 address
    """

    def clean(self, value):
        if (len(value) == 16 and isinstance(value, bytes)) or (
            not isinstance(value, bytes) and ":" in value
        ):
            return IPv6Parameter().clean(value)
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


class VLANIDParameter(IntParameter):
    """
    Check value is VLAN ID
    """

    def __init__(self, required=True, default=None):
        super().__init__(required=required, default=default, min_value=1, max_value=4095)


class VLANStackParameter(ListOfParameter):
    """
    Check value is a stack of of VLAN ID
    """

    def __init__(self, required=True, default=None):
        super().__init__(element=IntParameter(), required=required, default=default, convert=True)

    def clean(self, value):
        value = super().clean(value)
        if len(value) > 0:
            value[0] = VLANIDParameter().clean(value[0])
        for i in range(1, len(value)):
            value[i] = IntParameter(min_value=0, max_value=4095).clean(value[i])
        return value


class IntEnumParameter(IntParameter):
    """Check Parameter on Enum class"""

    def __init__(self, enum, required=True, default=None):
        self.enum = enum
        super().__init__(required=required, default=default)

    def clean(self, value):
        if isinstance(value, self.enum):
            return value
        value = super().clean(value)
        return self.enum(value)


class VLANIDListParameter(ListOfParameter):
    """
    Check value is a list of arbitrary vlans
    """

    def __init__(self, required=True, default=None):
        super().__init__(element=VLANIDParameter(), required=required, default=default)


class VLANIDMapParameter(StringParameter):
    """
    Check value is vlan map/vc filter
    """

    def clean(self, value):
        if isinstance(value, str) and not value.strip():
            return ""
        vp = VLANIDParameter()
        try:
            return list_to_ranges([vp.clean(v) for v in ranges_to_list(value)])
        except SyntaxError:
            self.raise_error(value)


class MACAddressParameter(StringParameter):
    """
    Check value is MAC address
    """

    def __init__(self, required=True, default=None, accept_bin=True):
        self.accept_bin = accept_bin
        super().__init__(required=required, default=default)

    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        if isinstance(value, str):
            value = super().clean(value)
        if not self.accept_bin and len(value) <= 6:
            self.raise_error(value)
        try:
            return str(MAC(value))
        except ValueError:
            self.raise_error(value)


class DiscriminatorParameter(StringParameter):
    """
    Check value is Cross Discriminator
    """

    def clean(self, value):
        try:
            discriminator(value)
            return value
        except ValueError as e:
            self.raise_error("Bad discriminator: %s" % str(e))


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
        >>> RDParameter().clean("15.37977:999")
        '1021017:999'
        """
        try:
            left, right = value.split(":", 1)
            right = int(right)
        except ValueError:
            self.raise_error(value)
        if right < 0:
            self.raise_error(value)
        if "." in left and left.count(".") == 1:
            # Type 2 notation
            hleft, lleft = left.split(".")
            try:
                left = str((int(hleft) << 16) + int(lleft))
            except ValueError:
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


class ObjectIdParameter(REStringParameter):
    def __init__(self, required=True, default=None):
        super().__init__("^[0-9a-f]{24}$", required=required, default=default)


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
        elif isinstance(value, str):
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
        super().__init__(required=required)
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


DocFieldMap = {"FloatField": FloatParameter(), "ReferenceField": ObjectIdParameter()}


class DocumentParameter(Parameter):
    """
    Document reference parameter
    """

    def __init__(self, document, required=True):
        super().__init__(required=required)
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
        super().__init__(required=required)
        self.document = document

    def clean(self, value):
        if not value:
            if self.required:
                self.raise_error("Value required")
            else:
                return None
        if not isinstance(value, dict):
            self.raise_error(value, "Value must be list dict")
        for k, v in self.document._fields.items():
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
            v = [smart_text(v).strip() for v in value]
            return [x for x in v if x]
        elif isinstance(value, str):
            v = [smart_text(x.strip()) for x in value.split(",")]
            return [x for x in v if x]
        else:
            self.raise_error("Invalid tags: %s" % value)


class ColorParameter(Parameter):
    def clean(self, value):
        if value is None and self.default is not None:
            return self.default
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            if value.startswith("#"):
                value = value[1:]
                if len(value) == 6:
                    try:
                        return int(value, 16)
                    except ValueError:
                        self.raise_error(value)
            try:
                return int(value, 10)
            except ValueError:
                self.raise_error(value)
        self.raise_error(value)


class ASNParameter(IntParameter):
    """Check Value is ASN Number"""

    def __init__(self, required=True, default=None):
        super().__init__(required=required, default=default, min_value=1, max_value=4_294_967_295)

    def clean(self, value):
        if isinstance(value, str) and "." in value:
            # 4-bytes asdot notation
            m, asn = value.split(".")
            value = int(m) * 65536 + int(asn)
        return super().clean(value)


# Patterns
OBJECT_ID = "[0-9a-f]{24}"
