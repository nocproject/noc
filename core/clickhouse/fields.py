# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Clickhouse field types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python collections
import itertools
from functools import partial
import socket
import struct


class BaseField(object):
    """
    BaseField class for ClickHouse structure
    """
    FIELD_NUMBER = itertools.count()
    db_type = None
    default_value = ""

    def __init__(self, default=None, description=None):
        """

        :param default: Default field value (if value not set)
        :param description: Field description
        """
        self.field_number = next(self.FIELD_NUMBER)
        self.name = None
        self.default = default or self.default_value
        self.description = description
        self.is_agg = False

    def contribute_to_class(self, cls, name):
        """
        Install field to model
        :param cls:
        :param name:
        :return:
        """
        cls._fields[name] = self
        cls._fields[name].name = name
        cls._tsv_encoders[name] = lambda record: self.to_tsv(record.get(name))

    def get_create_sql(self):
        """
        Return query for table create query. Example:

            CounterID UInt32,
            StartDate Date,

        :return:
        """
        return "%s %s" % (self.name, self.get_db_type())

    def get_db_type(self):
        """
        Return Field type. Use it in create query
        :return:
        """
        return self.db_type

    def to_tsv(self, value):
        """
        Use method when field convert to tsv format (ex. export)
        :param value:
        :return:
        """
        if value is None:
            return str(self.default_value)
        else:
            return str(value)

    def to_tsv_array(self, value):
        """
        Use method when field include in array
        :param value:
        :return:
        """
        return "'%s'" % self.to_tsv(value)


class StringField(BaseField):
    db_type = "String"
    default_value = ""


class DateField(BaseField):
    db_type = "Date"
    default_value = "0000-00-00"

    def to_tsv(self, value):
        if value is None:
            return self.default_value
        else:
            return value.strftime("%Y-%m-%d")


class DateTimeField(BaseField):
    db_type = "DateTime"
    default_value = "0000-00-00 00:00:00"

    def to_tsv(self, value):
        if value is None:
            return self.default_value
        else:
            return value.strftime("%Y-%m-%d %H:%M:%S")


class UInt8Field(BaseField):
    db_type = "UInt8"
    default_value = 0

    def to_tsv_array(self, value):
        if value is None:
            return str(self.default_value)
        else:
            return str(value)


class UInt16Field(UInt8Field):
    db_type = "UInt16"


class UInt32Field(UInt8Field):
    db_type = "UInt32"


class UInt64Field(UInt8Field):
    db_type = "UInt64"


class Int8Field(UInt8Field):
    db_type = "Int8"


class Int16Field(UInt8Field):
    db_type = "Int16"


class Int32Field(UInt8Field):
    db_type = "Int32"


class Int64Field(UInt8Field):
    db_type = "Int64"


class Float32Field(BaseField):
    db_type = "Float32"
    default_value = 0

    def to_tsv_array(self, value):
        if value is None:
            return str(self.default_value)
        else:
            return str(value)


class Float64Field(Float32Field):
    db_type = "Float64"


class BooleanField(UInt8Field):
    def to_tsv(self, value):
        return "1" if value else "0"

    def to_tsv_array(self, value):
        return "'1'" if value else "'0'"


class ArrayField(BaseField):
    def __init__(self, field_type, description=None):
        super(ArrayField, self).__init__(description=description)
        self.field_type = field_type

    def to_tsv(self, value):
        r = ["["]
        r += [",".join(self.field_type.to_tsv_array(v) for v in value)]
        r += ["]"]
        return "".join(r)

    def get_db_type(self):
        return "Array(%s)" % self.field_type.get_db_type()


class ReferenceField(BaseField):
    db_type = "UInt64"
    default_value = 0
    SELF_REFERENCE = "self"

    def __init__(self, dict_type, description=None, model=None):
        super(ReferenceField, self).__init__()
        self.is_self_reference = dict_type == self.SELF_REFERENCE
        self.dict_type = dict_type
        self.description = description
        self.model = model

    def to_tsv(self, value):
        if value is None:
            return str(self.default_value)
        else:
            return str(value.bi_id)


class IPv4Field(BaseField):
    db_type = "UInt32"

    def to_tsv(self, value):
        """
        Convert IPv4 as integer
        :param value:
        :return:
        """
        if value is None:
            return "0"
        else:
            return str(struct.unpack("!I", socket.inet_aton(value))[0])


class AggregatedField(BaseField):
    def __init__(self, field_type, agg_functions, description=None, f_expr=""):
        super(AggregatedField, self).__init__(description=description)
        self.field_type = field_type
        self.is_agg = True
        self.agg_functions = agg_functions
        self.f_expr = f_expr

    def to_tsv(self, value):
        return self.field_type.to_tsv()

    @property
    def db_type(self):
        return self.field_type.db_type

    def get_create_sql(self):
        pass

    def get_expr(self, function, f_param):
        return self.f_expr.format(p={"field": self.name,
                                     "function": function,
                                     "f_param": f_param})


class NestedField(ArrayField):
    db_type = "Nested"

    def __init__(self, field_type, description=None, *args):
        super(NestedField, self).__init__(field_type=field_type, description=description)
        # Skip field counters for nested fields
        for n in self.field_type._fields:
            next(self.FIELD_NUMBER)

    def contribute_to_class(self, cls, name):
        def get_tsv_encoder(fld, name, nested_name):
            def get(record):
                data = record.get(name, [])
                r = [
                    "[",
                    ",".join(fld.to_tsv_array(x.get(nested_name)) for x in data),
                    "]"
                ]
                return "".join(r)

            return get

        n_attrs = self.field_type._fields_order
        for n, nested_name in enumerate(n_attrs):
            field = "%s.%s" % (name, nested_name)
            cls._fields[field] = self.field_type._fields[nested_name]
            cls._fields[field].name = field
            cls._fields[field].field_number = self.field_number + n + 1
            cls._fields[field].get_create_sql = partial(self.get_create_nested_sql, field, cls._fields[field].db_type)
            cls._tsv_encoders[field] = get_tsv_encoder(cls._fields[field], name, nested_name)

    def to_tsv(self, value):
        out = []
        for field_type in self.field_type._fields_order:
            r = ["["]
            r += [",".join(self.field_type._fields[field_type].to_tsv_array(v[field_type]) for v in value)]
            r += ["]"]
            out += ["".join(r)]
        # r = r[:-1]
        return "\t".join(out)

    def get_db_type(self):
        return "Nested (\n%s \n)" % self.field_type.get_create_sql()

    @staticmethod
    def get_create_nested_sql(name, type):
        return "`%s` Array(%s)" % (name, type)
