# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service control api
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import cStringIO
## NOC modules
from api import API, api


class CtlAPI(API):
    name = "ctl"

    @api
    def prof_start(self):
        """
        Start service profiling
        """
        import yappi
        if yappi.is_running():
            return "Already running"
        else:
            yappi.start()
            return "Profiling started"

    @api
    def prof_stop(self):
        """
        Stop service profiling
        """
        import yappi
        if yappi.is_running:
            yappi.stop()
            return "Profiling stopped"
        else:
            return "Not running"

    @api
    def prof_threads(self):
        """
        Return profile threads info
        """
        import yappi
        i = yappi.get_thread_stats()
        out = cStringIO.StringIO()
        i.print_all(out=out)
        return out.getvalue()

    @api
    def prof_funcs(self):
        """
        Return profile threads info
        """
        import yappi
        i = yappi.get_func_stats()
        out = cStringIO.StringIO()
        i.print_all(out=out)
        return out.getvalue()

    @api
    def open_manhole(self):
        """
        Open manhole
        """
        import manhole
        mh = manhole.install()
        return mh.uds_name
