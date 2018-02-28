# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Service control api
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import logging
# Third-party modules
import six
# NOC modules
from noc.config import config
from .api import API, api


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
        out = six.StringIO()
        i.print_all(out=out)
        return out.getvalue()

    @api
    def prof_funcs(self):
        """
        Return profile threads info
        """
        import yappi
        i = yappi.get_func_stats()
        out = six.StringIO()
        i.print_all(
            out=out,
            columns={
                0: ("name", 80),
                1: ("ncall", 10),
                2: ("tsub", 8),
                3: ("ttot", 8),
                4: ("tavg", 8)
            }
        )
        return out.getvalue()

    @api
    def open_manhole(self):
        """
        Open manhole
        """
        import manhole
        mh = manhole.install()
        return mh.uds_name

    @api
    def inc_verbosity(self):
        """
        Increase logging verbosity
        :return:
        """
        current_level = logging.root.getEffectiveLevel()
        new_level = max(logging.DEBUG, current_level - 10)
        self.logger.critical("Changing loglevel: %s -> %s", current_level, new_level)
        logging.root.setLevel(new_level)
        return new_level

    @api
    def dec_verbosity(self):
        """
        Decrease logging verbosity
        :return:
        """
        current_level = logging.root.getEffectiveLevel()
        new_level = min(logging.CRITICAL, current_level + 10)
        self.logger.critical("Changing loglevel: %s -> %s", current_level, new_level)
        logging.root.setLevel(new_level)
        return new_level

    @api
    def forensic_start(self):
        """
        Start forensic logging
        :return:
        """
        if not config.features.forensic:
            config.features.forensic = True
            return True
        else:
            return False

    @api
    def forensic_stop(self):
        """
        Start forensic logging
        :return:
        """
        if config.features.forensic:
            config.features.forensic = False
            return True
        else:
            return False
