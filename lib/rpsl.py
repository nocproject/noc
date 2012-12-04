# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Routing Policy Specification Language (RFC2622) routines
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

RPLS_IDENT = 20


def rpsl_format(rpsl, ident=None):
    """
    Idents RPSL by aligning left side of values
    Emply strings and strings without ':' are silently dropped
    >>> rpsl_format("key1: value1\\nkey2: value2\\n\\nto drop\\n",7)
    'key1:  value1\\nkey2:  value2\\n'
    """
    if ident is None:
        ident = RPLS_IDENT
    out = []
    mask = "%%-%ds%%s" % ident
    for l in [x for x in rpsl.split("\n") if ":" in x]:
        k, v = l.split(":", 1)
        out += [mask % (k.strip() + ":", v.strip())]
    return "\n".join(out) + "\n"
