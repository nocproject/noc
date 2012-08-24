# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNSServer model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import subprocess
## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from noc.settings import config
from noc.dns.generators import generator_registry
from noc.lib.fields import INETField

generator_registry.register_all()


class DNSServer(models.Model):
    """
    DNS Server is an database object representing real DNS server.

    :param name: Unique DNS server name (usually, FQDN)
    :param generator_name: Zone generator name (BINDv9)
    :param ip: Server's IP address
    :param description: Optional description
    :param location: Optional location
    :param provisioning: Optional string containing shell command for
        zone provisioning. Can contain expansion variables.
        See expand_vars for details
    :param autozones_path: Optional prefix for autozones in config files
    """
    class Meta:
        verbose_name = _("DNS Server")
        verbose_name_plural = _("DNS Servers")
        db_table = "dns_dnsserver"
        app_label = "dns"

    name = models.CharField(_("Name"), max_length=64, unique=True)
    generator_name = models.CharField(_("Generator"), max_length=32,
        choices=generator_registry.choices)
    ip = INETField(_("IP"), null=True, blank=True)
    description = models.CharField(_("Description"), max_length=128,
        blank=True, null=True)
    location = models.CharField(_("Location"), max_length=128,
        blank=True, null=True)
    provisioning = models.CharField(_("Provisioning"), max_length=128,
        blank=True, null=True,
        help_text=_("Script for zone provisioning"))
    autozones_path = models.CharField(_("Autozones path"), max_length=256,
        blank=True, null=True, default="autozones",
        help_text=_("Prefix for autozones in config files"))

    def __unicode__(self):
        if self.location:
            return u"%s (%s)" % (self.name, self.location)
        else:
            return self.name

    def expand_vars(self, s):
        """
        Expand string variables.

        :param s: String, possible containing expansion variables.

        Valid expansion variables are:

        * rsync -- path to _rsync_ binary
        * vcs_path -- path to VCS's binary (i.e. hg)
        * repo -- path to the repo
        * ns -- DNS server's name
        * ip -- DNS server's IP address
        """
        return s % {
            "rsync"    : config.get("path", "rsync"),
            "vcs_path" : config.get("cm", "vcs_path"),
            "repo"     : config.get("cm", "repo"),
            "ns"       : self.name,
            "ip"       : self.ip,
        }

    # @todo: use pyrule
    def provision_zones(self):
        if self.provisioning:
            env = os.environ.copy()
            env["RSYNC_RSH"] = config.get("path", "ssh")
            cmd = self.expand_vars(self.provisioning)
            retcode = subprocess.call(cmd, shell=True, env=env,
                cwd=os.path.join(config.get("cm", "repo"), "dns"))
            return retcode == 0

    @property
    def generator_class(self):
        """
        Property containing generator class
        """
        return generator_registry[self.generator_name]
