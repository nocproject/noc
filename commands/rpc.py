# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service documentation request handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import json
import sys
import random
# Third-party modules
import tornado.httpclient


def die(msg):
    print msg
    sys.exit(1)


def main():
    service, method = sys.argv[1].split(".", 1)
    # Resolve service
    client = tornado.httpclient.HTTPClient()
    try:
        response = client.fetch(
            "http://127.0.0.1:8500/v1/catalog/service/%s" % service
        )
        candidates = ["%s:%s" % (
            s.get("ServiceAddress", s.get("Address")),
            s.get("ServicePort")
        ) for s in json.loads(response.body)]
    except Exception, why:
        die("Cannot resolve service %s: %s" % (service, why))
    if len(candidates) < 1:
        die("Service not found")
    tid = 1
    api = service.split("-")[0]
    req = {"id": tid, "method": method, "params": sys.argv[2:]}
    svc = random.sample(candidates, 1)[0]
    try:
        response = client.fetch(
            "http://%s/api/%s/" % (svc, api),
            method="POST",
            body=json.dumps(req)
        )
    except Exception, why:
        die("Failed to call: %s" % why)
    data = json.loads(response.body)
    if data.get("error"):
        die("Error: %s" % data.get("error"))
    else:
        print data["result"]

if __name__ == "__main__":
    main()
