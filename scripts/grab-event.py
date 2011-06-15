#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Export old fm event as JSON
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import binascii
import re
import sys
## Third-party modules
import psycopg2
## NOC modules
import set_env
set_env.setup(use_django=True)

def usage():
    print "Usage: %s <event_id> [ ... <event_id>]" % sys.argv[0]
    sys.exit(1)


rx_unqoute=re.compile(r"\\x([0-9a-f][0-9a-f])",re.MULTILINE|re.DOTALL)


def bin_unquote(s):
    if isinstance(s, unicode):
        s = s.encode("utf-8")
    return rx_unqoute.sub(lambda x:hex_map[x.group(1)], str(s).replace(r"\\","\\x5c"))


def q(s):
    return s.replace("\n", "\\n").replace("\"", "\\\"").replace("\\", "\\\\")


def convert_event(cursor, event_id):
    # Check event exists
    cursor.execute("SELECT COUNT(*) FROM fm_event WHERE id=%s", [event_id])
    if cursor.fetchall()[0][0] != 1:
        print "Event not found: %s" % event_id
        sys.exit(2)
    # Get profile name
    cursor.execute("""SELECT mo.profile_name
                      FROM sa_managedobject mo JOIN fm_event e ON (e.managed_object_id = mo.id)
                      WHERE e.id = %s""", [event_id])
    profile = cursor.fetchall()[0][0]
    # Get event data
    cursor.execute("SELECT key, value FROM fm_eventdata WHERE event_id=%s and type='>'", [event_id])
    vars = {}
    for k, v in cursor.fetchall():
        vars[k] = bin_unquote(v)
    # Order keys
    keys = []
    lkeys = vars.keys()
    for k in ("source", "profile", "1.3.6.1.6.3.1.1.4.1.0"):
        if k in vars:
            keys += [k]
            lkeys.remove(k)
    keys += sorted(lkeys)
    # Build JSON
    r = ["    {"]
    r += ["        \"profile\": \"%s\"," % q(profile)]
    r += ["        \"raw_vars\": {"]
    x =[]
    for k in keys:
        x += ["            \"%s\": \"%s\"" % (q(k), q(binascii.b2a_qp(str(vars[k]))))]
    r += [",\n".join(x)]
    r += ["        }"]
    r += ["    }"]
    return "\n".join(r)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        usage()
    from django.db import connection
    cursor = connection.cursor()
    print "[\n" + ",\n\n".join([convert_event(cursor, int(e)) for e in sys.argv[1:]]) + "\n]\n"
