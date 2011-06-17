#!/usr/bin/env python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Export old fm event as JSON
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import sys
## Third-party modules
import psycopg2
## NOC modules
import set_env
set_env.setup(use_django=True)
from noc.lib.escape import fm_escape, fm_unescape, json_escape
from noc.fm.models import get_event

def usage():
    print "Usage: %s <event_id> [ ... <event_id>]" % sys.argv[0]
    sys.exit(1)


rx_unqoute = re.compile(r"\\x([0-9a-f][0-9a-f])",re.MULTILINE|re.DOTALL)
rx_objectid = re.compile("^[0-9a-f]{24}$") 


def bin_unquote(s):
    if isinstance(s, unicode):
        s = s.encode("utf-8")
    return rx_unqoute.sub(lambda x:hex_map[x.group(1)], str(s).replace(r"\\","\\x5c"))


def event_json(profile, vars):
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
    r += ["        \"profile\": \"%s\"," % json_escape(profile)]
    r += ["        \"raw_vars\": {"]
    x =[]
    for k in keys:
        x += ["            \"%s\": \"%s\"" % (json_escape(k),
                                              json_escape(fm_escape(vars[k])))]
    r += [",\n".join(x)]
    r += ["        }"]
    r += ["    }"]
    return "\n".join(r)


def convert_old_event(cursor, event_id):
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
    return event_json(profile, vars)


def convert_new_event(event_id):
    event = get_event(event_id)
    if not event:
        raise Exception("Event not found: %s" % event_id)
    vars = dict([(k, fm_unescape(v)) for k, v in event.raw_vars.items()])
    return event_json(event.managed_object.profile_name, vars)


def convert_event(cursor, event_id):
    if rx_objectid.match(event_id):
        return convert_new_event(event_id)
    else:
        return convert_old_event(cursor, int(event_id))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        usage()
    from django.db import connection
    cursor = connection.cursor()
    print "[\n" + ",\n\n".join([convert_event(cursor, e) for e in sys.argv[1:]]) + "\n]\n"
