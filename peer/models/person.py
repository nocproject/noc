# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Person models
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
## NOC modules
from rir import RIR
from noc.core.gridvcs.manager import GridVCSField
from noc.lib.rpsl import rpsl_format, rpsl_multiple


class Person(models.Model):
    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Persons"
        db_table = "peer_person"
        app_label = "peer"

    nic_hdl = models.CharField("nic-hdl", max_length=64, unique=True)
    person = models.CharField("person", max_length=128)
    type = models.CharField("type", max_length=1, default="P",
        choices=[("P", "Person"), ("R", "Role")])
    address = models.TextField("address")
    phone = models.TextField("phone")
    fax_no = models.TextField("fax-no", blank=True, null=True)
    email = models.TextField("email")
    rir = models.ForeignKey(RIR, verbose_name="RIR")
    extra = models.TextField("extra", blank=True, null=True)
    rpsl = GridVCSField("rpsl_person")

    def __unicode__(self):
        return u" %s (%s)" % (self.nic_hdl, self.person)

    def get_rpsl(self):
        s = []
        if self.type == "R":
            s += ["role: %s" % self.person]
        else:
            s += ["person: %s" % self.person]
        s += ["nic-hdl: %s" % self.nic_hdl]
        s += rpsl_multiple("address", self.address)
        s += rpsl_multiple("phone", self.phone)
        s += rpsl_multiple("fax-no", self.fax_no)
        s += rpsl_multiple("email", self.email)
        if self.extra:
            s += [self.extra]
        return rpsl_format("\n".join(s))

    def touch(self):
        c_rpsl = self.rpsl.read()
        n_rpsl = self.get_rpsl()
        if c_rpsl == n_rpsl:
            return  # Not changed
        self.rpsl.write(n_rpsl)
        # todo: sliding job


##
## Signal handlers
##
@receiver(post_save, sender=Person)
def on_save(sender, instance, created, **kwargs):
    instance.touch()
