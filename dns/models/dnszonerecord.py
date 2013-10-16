# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNSZoneRecord model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
## NOC modules
from dnszone import DNSZone
from noc.lib.fields import TagsField
from noc.lib.app.site import site


class DNSZoneRecord(models.Model):
    """
    Zone RRs
    """
    class Meta:
        verbose_name = _("DNS Zone Record")
        verbose_name_plural = _("DNS Zone Records")
        db_table = "dns_dnszonerecord"
        app_label = "dns"

    zone = models.ForeignKey(DNSZone, verbose_name="Zone")
    name = models.CharField(_("Name"), max_length=64, blank=True, null=True)
    ttl = models.IntegerField(_("TTL"), null=True, blank=True)
    type = models.CharField(_("Type"), max_length=16)
    priority = models.IntegerField(_("Priority"), null=True, blank=True)
    content = models.CharField(_("Content"), max_length=256)
    tags = TagsField(_("Tags"), null=True, blank=True)

    def __unicode__(self):
        return u"%s %s" % (self.zone.name,
            " ".join([x
                      for x
                      in (self.name, self.type, self.content)
                      if x
                    ]))

    def get_absolute_url(self):
        """Return link to zone preview

        :return: URL
        :rtype: String
        """
        return site.reverse("dns:dnszone:change", self.zone.id)

##
## Signal handlers
##
@receiver(post_save, sender=DNSZoneRecord)
def on_save(sender, instance, created, **kwargs):
    instance.zone.touch(instance.zone.name)


@receiver(pre_delete, sender=DNSZoneRecord)
def on_delete(sender, instance, **kwargs):
    instance.zone.touch(instance.zone.name)
