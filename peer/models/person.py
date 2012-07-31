# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Person models
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
## NOC modules
from rir import RIR
from noc.lib.rpsl import rpsl_format


class Person(models.Model):
    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Persons"
        db_table = "peer_person"
        app_label = "peer"


    nic_hdl = models.CharField("nic-hdl", max_length=64, unique=True)
    person = models.CharField("person", max_length=128)
    address = models.TextField("address")
    phone = models.TextField("phone")
    fax_no = models.TextField("fax-no", blank=True, null=True)
    email = models.TextField("email")
    rir = models.ForeignKey(RIR, verbose_name="RIR")
    extra = models.TextField("extra", blank=True, null=True)

    def __unicode__(self):
        return u" %s (%s)" % (self.nic_hdl, self.person)

    @property
    def rpsl(self):
        s = []
        s += ["person: %s" % self.person]
        s += ["nic-hdl: %s" % self.nic_hdl]
        s += ["address: %s" % x for x in self.address.split("\n")]
        s += ["phone: %s" % x for x in self.phone.split("\n")]
        if self.fax_no:
            s += ["fax-no: %s" % x for x in self.fax_no.split("\n")]
        s += ["email: %s" % x for x in self.email.split("\n")]
        if self.extra:
            s += [self.extra]
        return rpsl_format("\n".join(s))
