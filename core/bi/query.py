# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Clickhouse query engine
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import six
# Python modules
from noc.core.clickhouse.dictionary import Dictionary
from noc.models import get_model


class OP(object):
    """
    :param min: Minimal count element in query
    :param max: Maximal count element in query
    :param convert: Convert function name
    """
    def __init__(self, min=None, max=None, join=None,
                 prefix=None, convert=None, function=None):
        self.min = min
        self.max = max
        self.join = join
        self.prefix = prefix
        self.convert = convert
        self.function = function

    def to_sql(self, seq):
        if self.min and len(seq) < self.min:
            raise ValueError("Missed argument: %s" % seq)
        if self.max and len(seq) > self.max:
            raise ValueError("Too many arguments: %s" % seq)
        if self.convert:
            return self.convert(seq)
        else:
            r = ["(%s)" % to_sql(x) for x in seq]
            if self.join:
                r = self.join.join(r)
            elif self.function:
                r = "%s(%s)" % (self.function, ", ".join(r))
            else:
                r = r[0]
            if self.prefix:
                r = "%s%s" % (self.prefix, r)
            return r


def f_lookup(seq):
    """
    $lookup (dictionary, id [,field])
    :param seq:
    :return:
    """
    dict_name = seq[0]
    dc = Dictionary.get_dictionary_class(dict_name)
    if len(seq) == 2:
        field_name = dc._fields_order[0]
    else:
        field_name = seq[2]
    t = dc.get_field_type(field_name)
    id_expr = to_sql(seq[1])
    return "dictGet%s('%s', '%s', %s)" % (t, dict_name, field_name, id_expr)


def in_lookup(seq):
    """
    $lookup (field, expr)
    :param seq:
    :return:
    """
    s3 = " NOT" if ("$not" in seq) or ("$NOT" in seq) else ""
    # check int
    m = []
    for l in seq[1]:
        if type(l) in six.integer_types or l.isdigit():
            m += [int(l)]
            continue
    if len(seq[1]) == 1:
        return "%s%s IN %s" % (seq[0]["$field"], s3, m[0])
    else:
        return "%s%s IN %s" % (seq[0]["$field"], s3, tuple(m))


def f_ternary_if(seq):
    """
    $?
    :param seq:
    :return:
    """
    return "((%s) ? (%s) : (%s))" % (to_sql(seq[0]),
                                     to_sql(seq[1]), to_sql(seq[2]))


def f_between(seq):
    """
    $between(a, b)
    :param seq:
    :return:
    """
    return "((%s) BETWEEN (%s) AND (%s))" % (
        to_sql(seq[0]), to_sql(seq[1]), to_sql(seq[2]))


def f_names(seq):
    """
    $names (dict, field)
    :param seq:
    :return:
    """
    return "arrayMap(k->dictGetString('%s', 'name', toUInt64(k)), dictGetHierarchy('%s', %s))" \
           % (seq[0], seq[0], seq[1])


def f_duration(seq):
    """
    $duration (dict, field)
    :param seq:
    :return:
    """
    return "SUM(arraySum(i -> ((i[2] > close_ts ? close_ts: i[2]) - (ts > i[1] ? ts: i[1]) < 0) ? 0 :" \
           " ((i[2] > close_ts ? close_ts: i[2]) - (ts > i[1] ? ts: i[1])), [%s]))" \
           % ",".join(seq)


def f_selector(seq):
    """
    $selector (expr, model, query)
    :param seq:
    :return:
    """
    expr, model_name, query = seq
    model = get_model(model_name)
    if not model:
        raise ValueError("Invalid model")
    if not hasattr(model, "get_bi_selector"):
        raise ValueError("Non-selectable model")
    ids = model.get_bi_selector(query)
    if ids:
        return "(%s IN (%s))" % (
            to_sql(expr),
            ",".join(str(i) for i in ids)
        )
    else:
        return "(0 = 1)"


def f_quantile(seq):

    return "quantile(%f)(%s)" % seq


OP_MAP = {
    # Comparison
    "$eq": OP(min=2, max=2, join=" = "),
    "$gt": OP(min=2, max=2, join=" > "),
    "$gte": OP(min=2, max=2, join=" >= "),
    "$lt": OP(min=2, max=2, join=" < "),
    "$lte": OP(min=2, max=2, join=" <= "),
    "$ne": OP(min=2, max=2, join=" != "),
    "$like": OP(min=2, max=2, join=" LIKE "),
    "$between": OP(min=3, max=3, convert=f_between),
    "$not": OP(min=1, max=1, function="NOT"),
    # @todo: a?b:c
    "$?": OP(min=3, max=3, convert=f_ternary_if),
    # Logical
    "$and": OP(min=1, join=" AND "),
    "$or": OP(min=1, join=" OR "),
    "$xor": OP(min=1, join=" XOR "),
    # Unary
    "$field": OP(min=1, max=1, convert=lambda x: escape_field(x[0])),
    "$neg": OP(min=1, max=1, prefix="-"),
    # Arithmetic
    "$plus": OP(min=2, max=2, join=" + "),
    "$minus": OP(min=2, max=2, join=" - "),
    "$mult": OP(min=2, max=2, join=" * "),
    "$div": OP(min=2, max=2, join=" / "),
    "$mod": OP(min=2, max=2, join=" % "),
    # Functions
    "$abs": OP(min=1, max=1, function="ABS"),
    "$now": OP(min=0, max=0, function="NOW"),
    # today
    # lower
    "$lower": OP(min=1, max=1, function="lowerUTF8"),
    # upper
    # substring
    # Aggregate functions
    "$count": OP(min=0, max=0, function="COUNT"),
    "$any": OP(min=1, max=1, function="ANY"),
    "$anylast": OP(min=1, max=1, function="ANYLAST"),
    "$min": OP(min=1, max=1, function="MIN"),
    "$max": OP(min=1, max=1, function="MAX"),
    "$sum": OP(min=1, max=1, function="SUM"),
    "$avg": OP(min=1, max=1, function="AVG"),
    "$uniq": OP(min=1, function="uniq"),
    "$empty": OP(min=1, function="empty"),
    "$notEmpty": OP(min=1, function="notEmpty"),
    "$position": OP(min=2, max=2, function="positionCaseInsensitiveUTF8"),
    "$median": OP(min=1, max=1, function="MEDIAN"),
    "$avgMerge": OP(min=1, max=1, function="avgMerge"),
    "$minMerge": OP(min=1, max=1, function="minMerge"),
    "$maxMerge": OP(min=1, max=1, function="maxMerge"),
    "$quantile": OP(min=2, max=2, function=f_quantile),
    # Dictionary lookup
    "$lookup": OP(min=2, max=3, convert=f_lookup),
    # List
    "$in": OP(min=2, max=3, convert=in_lookup),
    "$hierarchy": OP(min=2, max=2, function="dictGetHierarchy"),
    "$names": OP(min=2, max=2, convert=f_names),
    "$duration": OP(min=1, convert=f_duration),
    "$selector": OP(min=3, max=3, convert=f_selector)
}


def escape_str(s):
    return "%s" % s


def escape_field(s):
    return "%s" % s


def to_sql(expr):
    """
    Convert query expression to sql
    :param expr:
    :return:
    """
    if type(expr) == dict:
        for k in expr:
            op = OP_MAP.get(k)
            if not op:
                raise ValueError("Invalid operator: %s" % expr)
            v = expr[k]
            if type(v) != list:
                v = [v]
            return op.to_sql(v)
    elif isinstance(expr, six.string_types) and expr.isdigit():
        return int(expr)
    elif isinstance(expr, six.string_types):
        return "'%s'" % escape_str(expr)
    elif isinstance(expr, six.integer_types):
        return str(expr)
    elif isinstance(expr, float):
        return str(expr)
