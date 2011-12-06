# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Configuration file editor
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import ConfigParser
import os
import re
import pwd
## NOC modules
from noc.lib.app import Application, PermitSuperuser, view


class ConfigApplication(Application):
    """
    Configuration editor
    """
    title = "Configs"
    CONFIGS = ["noc.conf", "noc-launcher.conf", "noc-scheduler.conf",
               "noc-web.conf", "noc-sae.conf", "noc-activator.conf",
               "noc-classifier.conf", "noc-correlator.conf",
               "noc-notifier.conf", "noc-discovery.conf"]

    @view(url=r"^$", url_name="index", access=PermitSuperuser(),
          menu="Setup | Configs")
    def view_index(self, request):
        """
        List of configs
        """
        return self.render(request, "index.html", configs=self.CONFIGS)

    @view(url=r"^(?P<config>\S+)/$", url_name="view", access=PermitSuperuser())
    def view_config(self, request, config):
        """
        Display and edit config
        """
        def encode_name(section, name):
            return "%s::%s" % (section, name)

        def decode_name(name):
            return name.split("::")

        if config not in self.CONFIGS:
            return self.response_not_found("%s not found" % config)
        if request.POST:
            ## Attempt to save config
            conf = ConfigParser.RawConfigParser()
            for name, value in request.POST.items():
                if not value:
                    continue
                section, option = decode_name(name)
                if not conf.has_section(section):
                    conf.add_section(section)
                conf.set(section, option, value)
            with open(os.path.join("etc", config), "w") as f:
                conf.write(f)
            return self.response_redirect(request.path)
        ## Search for available online help
        help_path = "static/doc/en/nocbook/html/_sources/configuration.txt"
        help_prefix = config.replace(".", "-")
        help_href = "/static/doc/en/nocbook/html/configuration.html#%s"
        if os.path.exists(help_path):
            with open(help_path) as f:
                help = f.read()
        else:
            help = ""
        rx = re.compile(r"^\.\. _(%s.*?):" % help_prefix, re.MULTILINE)
        help = [x.replace("_", "-") for x in rx.findall(help)]
        ## Read config data
        conf = ConfigParser.RawConfigParser()
        conf.read(os.path.join("etc", config))
        read_only = not os.access(os.path.join("etc", config), os.W_OK)
        system_user = pwd.getpwuid(os.getuid())[0]
        defaults_conf = ConfigParser.RawConfigParser()
        defaults_conf.read(os.path.join("etc", "%s.defaults" % config[:-5]))
        sections = set(conf.sections())
        sections.update(defaults_conf.sections())
        data = []
        for s in sections:
            options = set()
            if conf.has_section(s):
                options.update(conf.options(s))
            if defaults_conf.has_section(s):
                options.update(defaults_conf.options(s))
            sd = []
            for o in options:
                x = {"name": encode_name(s, o), "label": o}
                if conf.has_option(s, o):
                    x["value"] = conf.get(s, o)
                else:
                    x["value"] = ""
                if defaults_conf.has_option(s, o):
                    x["default"] = defaults_conf.get(s, o)
                else:
                    x["default"] = ""
                # Try to find online help for option and determine option order
                option_help = "%s-%s-%s" % (
                help_prefix, s.replace("_", "-"), o.replace("_", "-"))
                try:
                    x["index"] = help.index(option_help)
                    x["help"] = help_href % option_help
                except ValueError:
                    x["index"] = 10000
                    x["help"] = None
                sd.append(x)
            # Order options like manual
            sd = sorted(sd, lambda x, y: cmp(x["index"], y["index"]))
            # Try to find online help for section and determine section order
            section_help = "%s-%s" % (help_prefix, s.replace("_", "-"))
            try:
                index = help.index(section_help)
                section_help = help_href % section_help
            except ValueError:
                index = 10000
                section_help = None
            data.append({"section": s, "data": sd, "help": section_help,
                         "index": index})
        # Order sections like manual
        data = sorted(data, lambda x, y: cmp(x["index"], y["index"]))
        return self.render(request, "view.html", config_name=config,
                data=data, read_only=read_only, system_user=system_user)
