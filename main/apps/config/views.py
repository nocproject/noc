# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.config application
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import ConfigParser
import hashlib
## NOC modules
from noc.lib.app import ExtApplication, view
from noc.lib.serialize import json_decode


class ConfigApplication(ExtApplication):
    """
    main.config application
    """
    title = "Configs"
    menu = "Setup | Configs"

    def __init__(self, *args, **kwargs):
        ExtApplication.__init__(self, *args, **kwargs)
        self.configs = {}  # id -> name
        self.config_list = []  # [{id: ..., name: ...}]
        self.defaults = {}  # id -> defaults path
        self.find_configs()

    def find_configs(self):
        def add_config(config, defaults):
            if config in seen:
                return
            h = hashlib.sha1(config).hexdigest()
            self.configs[h] = config
            self.config_list += [{"id": h, "name": config}]
            self.defaults[h] = defaults
            seen.add(config)

        seen = set()
        launcher_config = ConfigParser.SafeConfigParser()
        launcher_config.read("etc/noc-launcher.defaults")
        launcher_config.read("etc/noc-launcher.conf")
        add_config("etc/noc.conf", "etc/noc.defaults")
        add_config("etc/noc-launcher.conf",
            "etc/noc-launcher.defaults")
        for section in launcher_config.sections():
            if not section.startswith("noc-"):
                continue
            # Find daemon configs
            for opt in launcher_config.options(section):
                if opt.startswith("config"):
                    add_config(
                        launcher_config.get(section, opt),
                        "etc/%s.defaults" % section
                    )
        self.config_list = sorted(self.config_list,
            key=lambda x: x["name"])

    @view(url=r"^$", method=["GET"], access="launch", api=True)
    def api_configs(self, request):
        """
        Get Configs list
        :return:
        """
        return self.config_list

    @view(url=r"^(?P<id>[0-9a-f]{40})/$", method=["GET"],
        access="launch", api=True)
    def api_get_config(self, request, id):
        """
        Get Config data
        :param request:
        :param id:
        :return:
        """
        if id not in self.configs:
            return self.response_not_found()
        # Read config
        config = ConfigParser.SafeConfigParser()
        config.read(self.configs[id])
        # Read defaults
        defaults = ConfigParser.SafeConfigParser()
        defaults.read(self.defaults[id])
        # Build result
        r = []
        for ds in defaults.sections():
            for k, v in defaults.items(ds):
                if config.has_option(ds, k):
                    try:
                        vv = config.get(ds, k)
                    except ConfigParser.Error:
                        vv = ""  # Suppress interpolation errors
                else:
                    vv = ""
                r += [{
                    "section": ds,
                    "key": k,
                    "default": v,
                    "value": vv
                }]
        return r

    @view(url=r"^(?P<id>[0-9a-f]{40})/$", method=["POST"],
        access="launch", api=True)
    def api_save_config(self, request, id):
        """
        Get Config data
        :param request:
        :param id:
        :return:
        """
        data = json_decode(request.raw_post_data)
        if id not in self.configs:
            return self.response_not_found()
        # Read config
        config = ConfigParser.SafeConfigParser()
        config.read(self.configs[id])
        # Apply updates
        for d in data:
            if not config.has_section(d["section"]):
                config.add_section(d["section"])
            config.set(d["section"], d["key"], d["value"])
        # Save
        with open(self.configs[id], "w") as f:
            config.write(f)
        return True
