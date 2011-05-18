# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC.SAE.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import ConfigParser
## NOC modules
from noc.sa.script import NOCScript
from noc.sa.interfaces import IGetConfig
from noc.lib.fileutils import read_file

class Script(NOCScript):
    name="NOC.SAE.get_config"
    implements=[IGetConfig]
    
    def execute(self):
        # Load launcher config
        launcher_cfg = ConfigParser.SafeConfigParser()
        launcher_cfg.read("etc/noc-launcher.defaults")
        launcher_cfg.read("etc/noc-launcher.conf")
        # Build config list
        configs = set(["etc/noc-launcher.conf"])
        for daemon in ["noc-fcgi", "noc-scheduler", "noc-sae",
                       "noc-activator", "noc-classifier",
                       "noc-correlator", "noc-notifier", "noc-probe"]:
            if launcher_cfg.has_section(daemon):
                for c in [c for c in launcher_cfg.options(daemon)
                          if c == "config" or c.startswith("config.")]:
                    cfg = launcher_cfg.get(daemon, c, None)
                    if cfg:
                        configs.add(cfg)
        # Get configs
        cfg = []
        for c in sorted(configs):
            cf = read_file(c)
            if cf:
                cfg += [{
                    "name": c,
                    "config": cf
                }]
        return cfg