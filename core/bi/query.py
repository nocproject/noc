# ----------------------------------------------------------------------
# Clickhouse query engine
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from noc.core.bi.dictionaries.loader import loader
from noc.models import get_model
from noc.config import config


class OP(object):
    """
    :param min: Minimal count element in query
    :param max: Maximal count element in query
    :param convert: Convert function name
    """

    def __init__(self, min=None, max=None, join=None, prefix=None, convert=None, function=None):
        self.min = min
        self.max = max
        self.join = join
        self.prefix = prefix
        self.convert = convert
        self.function = function

    def to_sql(self, seq, model=None):
        if self.min and len(seq) < self.min:
            raise ValueError("Missed argument: %s" % seq)
        if self.max and len(seq) > self.max:
            raise ValueError("Too many arguments: %s" % seq)
        if self.convert:
            return self.convert(seq, model)
        r = ["(%s)" % to_sql(x, model=model) for x in seq]
        if self.join:
            r = self.join.join(r)
        elif self.function:
            r = "%s(%s)" % (self.function, ", ".join(r))
        else:
            r = r[0]
        if self.prefix:
            r = "%s%s" % (self.prefix, r)
        return r


def f_lookup(seq, model=None):
    """
    $lookup (dictionary, id [,field])
    :param seq:
    :param model
    :return:
    """
    dict_name = seq[0]
    if "." in dict_name:
        _, dict_name = dict_name.split(".", 1)
    dc = loader[dict_name]
    if len(seq) == 2:
        field_name = dc.get_pk_name()
    else:
        field_name = seq[2]
    t = dc.get_field_type(field_name)
    id_expr = to_sql(seq[1])
    return (
        f"dictGet{t}('{config.clickhouse.db_dictionaries}.{dict_name}', '{field_name}', {id_expr})"
    )


def in_lookup(seq, model=None):
    """
    $lookup (field, expr)
    :param seq:
    :param model:
    :return:
    """
    s3 = " NOT" if ("$not" in seq) or ("$NOT" in seq) else ""
    # check int
    m = []
    for item in seq[1]:
        if isinstance(item, int) or item.isdigit():
            m += [int(item)]
            continue
    if len(seq[1]) == 1:
        return "%s%s IN %s" % (seq[0]["$field"], s3, m[0])
    return "%s%s IN %s" % (seq[0]["$field"], s3, tuple(m))


def f_ternary_if(seq, model=None):
    """
    $?
    :param seq:
    :param model:
    :return:
    """
    return f"(({to_sql(seq[0])}) ? ({to_sql(seq[1])}) : ({to_sql(seq[2])}))"


def f_between(seq, model=None):
    """
    $between(a, b)
    :param seq:
    :param model:
    :return:
    """
    return f"(({to_sql(seq[0])}) BETWEEN ({to_sql(seq[1])}) AND ({to_sql(seq[2])}))"


def f_names(seq, model=None):
    """
    $names (dict, field)
    :param seq:
    :param model:
    :return:
    """
    dict_name = seq[0]
    if "." in dict_name:
        _, dict_name = dict_name.split(".", 1)
    return f"arrayMap(k->dictGetString('{config.clickhouse.db_dictionaries}.{dict_name}', 'name', toUInt64(k)), dictGetHierarchy('{config.clickhouse.db_dictionaries}.{dict_name}', {seq[1]}))"


def f_duration(seq, model=None):
    """
    $duration (dict, field)
    :param seq:
    :param model:
    :return:
    """
    return (
        "SUM(arraySum(i -> ((i[2] > close_ts ? close_ts: i[2]) - (ts > i[1] ? ts: i[1]) < 0) ? 0 :"
        " ((i[2] > close_ts ? close_ts: i[2]) - (ts > i[1] ? ts: i[1])), [%s]))" % ",".join(seq)
    )


def f_selector(seq, model=None):
    """
    $selector (expr, model, query)
    :param seq:
    :param model:
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
        return "(%s IN (%s))" % (to_sql(expr), ",".join(str(i) for i in ids))
    return "(0 = 1)"


def f_quantile(seq):
    return "quantile(%f)(%s)" % seq


def resolve_format(seq, model=None):
    if model and hasattr(model, "transform_field"):
        tf = getattr(model, "transform_field")
        return "%s" % tf(seq[0])
    return "%s" % seq[0]


def f_any(seq, model=None):
    if not isinstance(seq[1], list):
        seq[1] = [seq[1]]
    return "hasAny(%s, %s)" % (seq[0]["$field"], [str(x) for x in seq[1]])


def f_all(seq, model=None):
    if not isinstance(seq[1], list):
        seq[1] = [seq[1]]
    return "hasAll(%s, %s)" % (seq[0]["$field"], [str(x) for x in seq[1]])


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
    "$field": OP(min=1, max=1, convert=resolve_format),
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
    "$uniqExact": OP(min=1, function="uniqExact"),
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
    # Array
    "$hasAll": OP(min=2, max=2, convert=f_all),
    "$hasAny": OP(min=2, max=2, convert=f_any),
    # List
    "$in": OP(min=2, max=3, convert=in_lookup),
    "$hierarchy": OP(min=2, max=2, function="dictGetHierarchy"),
    "$names": OP(min=2, max=2, convert=f_names),
    "$duration": OP(min=1, convert=f_duration),
    "$selector": OP(min=3, max=3, convert=f_selector),
}


def escape_str(s):
    return "%s" % s


def escape_field(s):
    return "%s" % s


def to_sql(expr, model=None):
    """
    Convert query expression to sql
    :param expr:
    :param model:
    :return:
    """
    if isinstance(expr, dict):
        for k in expr:
            op = OP_MAP.get(k)
            if not op:
                raise ValueError("Invalid operator: %s" % expr)
            v = expr[k]
            if not isinstance(v, list):
                v = [v]
            return op.to_sql(v, model)
    elif isinstance(expr, str):
        if expr.isdigit():
            return int(expr)
        return "'%s'" % escape_str(expr)
    elif isinstance(expr, int):
        return str(expr)
    elif isinstance(expr, float):
        return str(expr)
