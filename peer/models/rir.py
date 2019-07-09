# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# RIR model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time

# Third-party modules
import six
from six.moves.urllib.parse import urlencode
from six.moves.urllib.request import urlopen
from six.moves.urllib.error import URLError
from django.db import models

# NOC modules
from noc.core.model.base import NOCModel
from noc.core.model.decorator import on_delete_check


class RIRDBUpdateError(Exception):
    pass


RIPE_SYNCUPDATES_URL = "https://syncupdates.db.ripe.net"


@on_delete_check(check=[("peer.Person", "rir"), ("peer.AS", "rir"), ("peer.Maintainer", "rir")])
@six.python_2_unicode_compatible
class RIR(NOCModel):
    """
    Regional internet registries
    """

    class Meta(object):
        verbose_name = "RIR"
        verbose_name_plural = "RIRs"
        db_table = "peer_rir"
        app_label = "peer"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    whois = models.CharField("Whois", max_length=64, blank=True, null=True)

    def __str__(self):
        return self.name

    def update_rir_db(self, data, maintainer=None):
        """
        Update RIR's database API and returns report

        :param data:
        :param maintainer:
        :return:
        """
        rir = "RIPE" if self.name == "RIPE NCC" else self.name
        return getattr(self, "update_rir_db_%s" % rir)(data, maintainer)

    def update_rir_db_RIPE(self, data, maintainer):
        """
        RIPE NCC Update API
        :param data:
        :param maintainer:
        :return:
        """
        data = [x for x in data.split("\n") if x]  # Strip empty lines
        if maintainer.password:
            data += ["password: %s" % maintainer.password]
        admin = maintainer.admins.all()[0]
        T = time.gmtime()
        data += ["changed: %s %04d%02d%02d" % (admin.email, T[0], T[1], T[2])]
        data += ["source: RIPE"]
        data = "\n".join(data)
        try:
            f = urlopen(url=RIPE_SYNCUPDATES_URL, data=urlencode({"DATA": data}))
            data = f.read()
        except URLError as why:
            data = "Update failed: %s" % why
        return data
