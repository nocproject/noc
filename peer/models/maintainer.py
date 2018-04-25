# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Peer module models
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from django.db import models
# NOC modules
from noc.core.crypto import md5crypt
from noc.lib.rpsl import rpsl_format
from noc.core.model.decorator import on_save
from noc.core.gridvcs.manager import GridVCSField
from .rir import RIR
from .person import Person


@on_save
class Maintainer(models.Model):
    class Meta(object):
        verbose_name = "Maintainer"
        verbose_name_plural = "Maintainers"
        db_table = "peer_maintainer"
        app_label = "peer"

    maintainer = models.CharField("mntner", max_length=64, unique=True)
    description = models.CharField("description", max_length=64)
    password = models.CharField("Password", max_length=64,
                                null=True, blank=True)
    rir = models.ForeignKey(RIR, verbose_name="RIR")
    admins = models.ManyToManyField(Person, verbose_name="admin-c")
    extra = models.TextField("extra", blank=True, null=True)
    rpsl = GridVCSField("rpsl_maintainer")

    def __unicode__(self):
        return self.maintainer

    def get_rpsl(self):
        s = []
        s += ["mntner: %s" % self.maintainer]
        s += ["descr: %s" % self.description]
        if self.password:
            s += ["auth: MD5-PW %s" % md5crypt(self.password)]
        s += ["admins: %s" % x.nic_hdl for x in self.admins.all()]
        s += ["mnt-by: %s" % self.maintainer]
        if self.extra:
            s += [self.extra]
        return rpsl_format("\n".join(s))

    def touch_rpsl(self):
        c_rpsl = self.rpsl.read()
        n_rpsl = self.get_rpsl()
        if c_rpsl == n_rpsl:
            return  # Not changed
        self.rpsl.write(n_rpsl)

    def on_save(self):
        self.touch_rpsl()
