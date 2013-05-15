# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Collect crashinfo files and create FM events
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import os
import stat
import cPickle
import datetime
## NOC modules
from noc.lib.scheduler.autointervaljob import AutoIntervalJob
from noc.lib.debug import DEBUG_CTX_CRASH_DIR, DEBUG_CTX_CRASH_PREFIX
from noc.settings import CRASHINFO_LIMIT
from noc.fm.models import NewEvent
from noc.sa.models import ManagedObject


class CollectCrashinfoJob(AutoIntervalJob):
    name = "main.collect_crashinfo"
    interval = 900
    randomize = True

    def handler(self, *args, **kwargs):
        # Check crashinfo directory exists
        if not os.path.isdir(DEBUG_CTX_CRASH_DIR):
            self.error("No crashinfo directory found: %s" % DEBUG_CTX_CRASH_DIR)
            return False
        # Look for existing crashinfos
        crashinfos = [fn for fn in os.listdir(DEBUG_CTX_CRASH_DIR)
                      if fn.startswith(DEBUG_CTX_CRASH_PREFIX)]
        if not crashinfos:
            return True
        # Process crashinfos
        sae = ManagedObject.objects.get(name="SAE")
        self.info("%d crashinfo files found. Importing" % len(crashinfos))
        failed = False
        for fn in crashinfos:
            path = os.path.join(DEBUG_CTX_CRASH_DIR, fn)
            # Check crashinfo access
            if not os.access(path, os.R_OK | os.W_OK):
                # Wait for noc-launcher to fix permissions
                self.error("Cannot access crashinfo '%s'."
                              "Left until noc-launcher will fix permissions" % fn)
                failed = True
                continue
            # Check crashinfo size
            if os.stat(path)[stat.ST_SIZE] > CRASHINFO_LIMIT:
                self.error("Too large crashinfo '%s'. Removing" % fn)
                os.unlink(path)
                continue
            # Decode crashinfo
            try:
                with open(path, "r") as f:
                    data = cPickle.loads(f.read())
            except OSError, why:
                self.error("Cannot load crashinfo '%s': %s" % (fn, why[0]))
                failed = True
                continue
            except MemoryError:
                self.error("Failed to allocate memory to import crashinfo '%s'" % fn)
                failed = True
                continue
            except:
                self.error("Cannot import crashinfo: %s" % path)
                failed = True
                continue
            # Write FM event
            ts = datetime.datetime.fromtimestamp(data["ts"])
            del data["ts"]
            try:
                NewEvent(
                    timestamp=ts,
                    managed_object=sae,
                    raw_vars=data,
                    log=[]
                ).save()
            except Exception, why:
                self.error("Failed to create FM event from crashinfo "
                              "'%s': %s" % (fn, why))
                failed = True
                continue
            # Remove crashinfo
            os.unlink(path)
        return not failed
