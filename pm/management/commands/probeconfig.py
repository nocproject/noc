# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ProbeConfig management
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from optparse import make_option
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.pm.models.probeconfig import ProbeConfig
from noc.pm.models.probe import Probe
from noc.lib.debug import error_report


class Command(BaseCommand):
    """
    Manage Jobs
    """
    help = "Manage Probe configs"
    option_list=BaseCommand.option_list+(
        make_option(
            "--list", "-l",
            action="store_const",
            dest="cmd",
            const="list",
            help="List configs"
        ),
        make_option(
            "--touch", "-t",
            action="store_const",
            dest="cmd",
            const="touch",
            help="Soft rebuild"
        ),
        make_option(
            "--rebuild", "-r",
            action="store_const",
            dest="cmd",
            const="rebuild",
            help="Rebuild configs"
        )
    )

    def handle(self, *args, **kwargs):
        try:
            self._handle(*args, **kwargs)
        except CommandError:
            raise
        except:
            error_report()

    def _handle(self, *args, **options):
        self.verbose = bool(options.get("verbosity"))
        if options["cmd"] == "list":
            return self.handle_list()
        elif options["cmd"] == "rebuild":
            return self.handle_rebuild()
        elif options["cmd"] == "touch":
            return self.handle_touch()

    def handle_list(self):
        def get_probe(p_id):
            n = p_cache.get(p_id)
            if not n:
                n = Probe.objects.get(id=p_id).name
                p_cache[p_id] = n
            return n

        p_cache = {}  # Probe id -> name
        for pc in ProbeConfig.objects.all():
            print "CONFIG: %s ID: %s (%s)" % (
                pc.model_id, pc.object_id, pc.uuid)
            if pc.is_deleted:
                print "    DELETED"
            else:
                # @todo: unicode(object)
                o = pc.get_object()
                if o:
                    print "    Object   : %s" % unicode(o)
                else:
                    print "    Object   : Missed object"
                xp = " (EXPIRED)" if pc.is_expired else ""
                print "    Changed  : %s Expire: %s%s" % (
                    pc.changed.isoformat(), pc.expire.isoformat(), xp)
                print "    Probe    : %s (instance %s)" % (
                    get_probe(pc.probe_id), pc.instance_id)
                print "    Handler  : %s" % pc.handler
                print "    Interval : %s" % pc.interval
                print "    Config   :"
                for k in pc.config:
                    print "             %20s: %s" % (k, pc.config[k])
                print "    Metrics  :"
                for m in pc.metrics:
                    print "               %s:" % m.metric
                    print "                   Type       : %s" % m.metric_type
                    print "                   Thresholds : %s" % "/".join(str(t) if t is not None else "-" for t in m.thresholds)
                    print "                   Convert    : %s X %s" % (m.convert, m.scale)
                    if m.collectors:
                        print "                   Collectors : %s (write concern %s)" % (m.collectors.policy, m.collectors.write_concern)
                        for c in m.collectors.collectors:
                            print "                       %s://%s:%s" % (c.proto, c.address, c.port)
                    else:
                        print "                   Collectors : Not configured"
            print

    def handle_rebuild(self):
        pass

    def handle_touch(self):
        for pc in ProbeConfig.objects.all():
            o = pc.get_object()
            if not o:
                # Missed object, mark as delete
                pc.changed = ProbeConfig.DELETE_DATE
                pc.expire = ProbeConfig.DELETE_DATE
                pc.save()
                continue
            if pc.model_id == "pm.MetricConfig":
                ProbeConfig._refresh_config(o)
            else:
                ProbeConfig._refresh_object(o)
