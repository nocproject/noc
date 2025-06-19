# ----------------------------------------------------------------------
# ClickHouse field types
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from ast import literal_eval
from datetime import datetime
from typing import Optional
import itertools
import socket
import struct
from collections import defaultdict


class BaseField(object):
    """
    BaseField class for ClickHouse structure
    """

    FIELD_NUMBER = itertools.count()
    db_type = None
    default_value = ""

    def __init__(
        self, default=None, description: Optional[str] = None, low_cardinality: bool = False
    ):
        """

        :param default: Default field value (if value not set)
        :param description: Field description
        :param low_cardinality: Enable low_cardinality for field
        """
        self.field_number = next(self.FIELD_NUMBER)
        self.name = None
        self.default = default or self.default_value
        self.description = description
        self.is_agg = False
        self.low_cardinality = low_cardinality

    def set_name(self, name):
        """
        Set field name according to model

        :param name: Field name
        :return:
        """
        self.name = name

    def iter_create_sql(self):
        """
        Yields (field name, db type) for all nested fields

        :return:
        """
        yield self.name, self.get_db_type()

    def get_db_type(self, name=None):
        """
        Return Field type. Use it in create query

        :param name: Optional nested field name
        :return:
        """
        if self.low_cardinality:
            return f"LowCardinality({self.db_type})"
        return self.db_type

    def get_displayed_type(self):
        """
        Return Field type for external application
        :return:
        """
        return self.db_type

    def apply_json(self, row_json, value):
        """
        Append converted `value` to `row _json` dict

        :param json: Row dict
        :param value: Raw value
        :return:
        """
        row_json[self.name] = self.to_json(value)

    def to_json(self, value):
        """
        Convert `value` to JSON-serializeable format

        :param value: Input value
        :return: JSON-serializable value
        """
        if value is None:
            return self.default_value
        return str(value)

    def to_python(self, value):
        """
        Use method when field convert to python object
        :param value:
        :return:
        """
        return value

    def get_select_sql(self):
        return self.name

    @staticmethod
    def nested_path(name):
        """
        Split nested path to field name and nested name

        :param name: Nested field name
        :return: (Field name, Nested name)
        """
        name = name.strip("`")
        if "." in name:
            return name.split(".", 1)
        return name, None


class StringField(BaseField):
    db_type = "String"
    default_value = ""


class DateField(BaseField):
    db_type = "Date"
    default_value = "0000-00-00"

    def to_json(self, value):
        if value is None:
            return self.default_value
        return value.strftime("%Y-%m-%d")

    def to_python(self, value):
        if not value or value == self.default_value or value == "1970-01-01":
            return None
        else:
            return datetime.strptime(value, "%Y-%m-%d").date()


class DateTimeField(BaseField):
    db_type = "DateTime"
    default_value = "0000-00-00 00:00:00"

    def to_json(self, value):
        if value is None:
            return self.default_value
        return value.strftime("%Y-%m-%d %H:%M:%S")

    def to_python(self, value):
        if not value or value == self.default_value or value == "1970-01-01 00:00:00":
            return None
        else:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")


class UInt8Field(BaseField):
    db_type = "UInt8"
    default_value = 0

    def to_json(self, value):
        if value is None:
            return self.default_value
        return int(value)

    def to_python(self, value):
        if not value:
            return self.default_value
        return int(value)


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
    default_value = 0.0

    def to_json(self, value):
        if value is None:
            return self.default_value
        return float(value)

    def to_python(self, value):
        if not value:
            return self.default_value
        return float(value)


class Float64Field(Float32Field):
    db_type = "Float64"


class BooleanField(UInt8Field):
    def to_json(self, value):
        return 1 if value else 0

    def to_python(self, value):
        if not value:
            return False
        return value == "1"


class ArrayField(BaseField):
    def __init__(self, field_type, description=None):
        super().__init__(description=description)
        self.field_type = field_type

    def to_json(self, value):
        return [self.field_type.to_json(v) for v in value]

    def get_db_type(self, name=None):
        return f"Array({self.field_type.get_db_type()})"

    def get_displayed_type(self):
        return "Array(%s)" % self.field_type.get_db_type()

    def to_python(self, value):
        if not value or value == "[]":
            return []
        return [self.field_type.to_python(x.strip("'\" ")) for x in value[1:-1].split(",")]


class MaterializedField(BaseField):
    def __init__(self, field_type, expression, description=None, low_cardinality=True):
        super().__init__(description=description, low_cardinality=low_cardinality)
        self.field_type = field_type
        self.expression = expression

    def get_db_type(self, name=None):
        return self.field_type.get_db_type()

    def iter_create_sql(self):
        yield self.name, f"{self.get_db_type()} MATERIALIZED {self.expression}"


class ReferenceField(BaseField):
    db_type = "UInt64"
    default_value = 0
    SELF_REFERENCE = "self"

    def __init__(self, dict_type, description=None, model=None, low_cardinality=False):
        super().__init__(description=description, low_cardinality=low_cardinality)
        self.is_self_reference = dict_type == self.SELF_REFERENCE
        self.dict_type = dict_type
        self.model = model
        if self.low_cardinality:
            self.db_type = "String"

    def to_json(self, value):
        if value is None:
            return self.default_value
        if self.low_cardinality:
            return value
        return value.bi_id


class IPv4Field(BaseField):
    db_type = "UInt32"

    def to_json(self, value):
        """
        Convert IPv4 as integer

        :param value:
        :return:
        """
        if value is None:
            return 0
        return struct.unpack("!I", socket.inet_aton(value))[0]

    def to_python(self, value):
        if value is None:
            return "0"
        return socket.inet_ntoa(struct.pack("!I", int(value)))

    def get_displayed_type(self):
        return "IPv4"


class IPv6Field(BaseField):
    db_type = "UInt128"

    def to_json(self, value):
        """
        Convert IPv6 as integer

        :param value:
        :return:
        """
        if value is None:
            return 0
        return struct.unpack("!I", socket.inet_aton(value))[0]

    def to_python(self, value):
        if value is None:
            return "0"
        return socket.inet_ntoa(struct.pack("!I", int(value)))

    def get_displayed_type(self):
        return "IPv6"


class AggregatedField(BaseField):
    def __init__(self, expression, field_type, agg_function, params=None, description=None):
        super().__init__(description=description)
        self.field_type = field_type
        self.agg_function = agg_function
        self.expression = expression
        self.params = params

    def to_json(self, value):
        return self.field_type.to_json(value)

    def get_db_type(self, name=None):
        return f"AggregateFunction({self.agg_function}, {self.agg_function.get_db_type(self.field_type)})"

    def get_expression(self, combinator: str = None):
        return self.agg_function.get_expression(self, combinator)
        # return self.f_expr.format(p={"field": self.name, "function": function, "f_param": f_param})
        # return "{p[function]}Merge({p[field]}_{p[function]})"


class MapField(BaseField):
    def __init__(self, field_type, description=None):
        super().__init__(description=description)
        self.field_type = field_type

    def to_json(self, value):
        if not isinstance(value, dict):
            raise ValueError("Value for Map Field Must be Dict")
        return value

    def get_db_type(self, name=None):
        return f"Map(String, {self.field_type.get_db_type()})"

    def get_displayed_type(self):
        return "Nested"


class NestedField(ArrayField):
    db_type = "Nested"

    def iter_create_sql(self):
        for nested_field in self.field_type._meta.ordered_fields:
            yield f"{self.name}.{nested_field.name}", self.get_db_type(nested_field.name)

    def apply_json(self, row_json, value):
        arrays = defaultdict(list)
        for item in value:
            row = {}
            for f in item:
                self.field_type._meta.fields[f].apply_json(row, item[f])
            for nested_name in row:
                full_name = "%s.%s" % (self.name, nested_name)
                arrays[full_name] += [row[nested_name]]
        row_json.update(arrays)

    def get_db_type(self, name=None):
        if name is None:
            return "Nested (\n%s \n)" % self.field_type.get_create_sql()
        return "Array(%s)" % self.field_type._meta.fields[name].get_db_type()

    def get_displayed_type(self):
        return "Nested (\n%s \n)" % self.field_type.get_create_sql()

    def to_python(self, value):
        if not value or value == "[]":
            return []
        value = literal_eval(value)
        return [
            {
                f.name: f.to_python(v.strip("'"))
                for f, v in (dict(zip(self.field_type._meta.ordered_fields, v)).items())
            }
            for v in value
        ]

    def get_select_sql(self):
        m = [
            "toString(%s.%s[x])" % (self.name, f.name) for f in self.field_type._meta.ordered_fields
        ]
        r = [
            "arrayMap(x -> [%s], arrayEnumerate(%s.%s))"
            % (",".join(m), self.name, self.field_type.get_pk_name())
        ]
        return "".join(r)
