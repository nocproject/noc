# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# RIR model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import urllib
import urllib2
# Django modules
from django.db import models


class RIRDBUpdateError(Exception):
    pass

# Check ssl library is available
try:
    import ssl
    # Use SSL-enabled version when possible
    RIPE_SYNCUPDATES_URL = "https://syncupdates.db.ripe.net"
except ImportError:
    RIPE_SYNCUPDATES_URL = "http://syncupdates.db.ripe.net"


class RIR(models.Model):
    """
    Regional internet registries
    """
    class Meta:
        verbose_name = "RIR"
        verbose_name_plural = "RIRs"
        db_table = "peer_rir"
        app_label = "peer"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    whois = models.CharField("Whois", max_length=64,
        blank=True, null=True)

    def __unicode__(self):
        return self.name

    # Update RIR's database API and returns report
    def update_rir_db(self, data, maintainer=None):
        rir = "RIPE" if self.name == "RIPE NCC" else self.name
        return getattr(self, "update_rir_db_%s" % rir)(data, maintainer)

    # RIPE NCC Update API
    def update_rir_db_RIPE(self, data, maintainer):
        data = [x for x in data.split("\n") if x]  # Strip empty lines
        if maintainer.password:
            data += ["password: %s" % maintainer.password]
        admin = maintainer.admins.all()[0]
        T = time.gmtime()
        data += ["changed: %s %04d%02d%02d" % (admin.email, T[0], T[1], T[2])]
        data += ["source: RIPE"]
        data = "\n".join(data)
        try:
            f = urllib2.urlopen(url=RIPE_SYNCUPDATES_URL,
                                data=urllib.urlencode({"DATA": data}))
            data = f.read()
        except urllib2.URLError, why:
            data = "Update failed: %s" % why
        return data
