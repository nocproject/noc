# ---------------------------------------------------------------------
# Pretty JSON formatter
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from bson.binary import Binary
from functools import reduce

# NOC modules
from noc.core.escape import json_escape
from noc.core.text import indent


class PrettyJSON(object):
    @classmethod
    def to_json(cls, o, order=None) -> str:
        r = cls.convert(o, 0, order)
        if not r.endswith("\n"):
            r += "\n"
        return r

    @classmethod
    def convert(cls, o, i, order=None):
        if o is None:
            return indent("null", i)
        if isinstance(o, str):
            return indent('"%s"' % json_escape(o), i)
        elif isinstance(o, bool):
            return indent("true" if o else "false", i)
        elif isinstance(o, int):
            return indent("%d" % o, i)
        elif isinstance(o, float):
            return indent(str(o), i)
        elif isinstance(o, Binary) and o.subtype in (3, 4):  # uuid field
            return indent('"%s"' % o.as_uuid(o.subtype), i)
        elif isinstance(o, list):
            if len(o) == 0:
                return indent("[]", i)
            t = [cls.convert(e, 0, order) for e in o]
            lt = reduce(lambda x, y: x + y, [len(x) for x in t])
            lt += i + (len(o) - 1) * 2
            if lt > 72:
                # Long line
                r = [indent("[", i)]
                r += [",\n".join(indent(x, i + 4) for x in t)]
                r += [indent("]", i)]
                return "\n".join(r)
            else:
                r = "[%s]" % ", ".join(t)
                return indent(r, i)
        elif isinstance(o, dict):
            if not o:
                return indent("{}", i)
            keys = sorted(o)
            if order:
                nk = [k for k in order if k in keys]
                nk += [k for k in keys if k not in order]
                keys = nk
            r = ",\n".join(
                f"{cls.convert(k, 0, order)}: {cls.convert(o[k], 0, order)}" for k in keys
            )
            return indent("{\n%s\n}" % indent(r, 4), i)
        raise ValueError("Cannot encode %r" % o)


to_json = PrettyJSON.to_json
