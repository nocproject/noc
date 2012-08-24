# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DNSZoneRecordType model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from noc.lib.validators import check_re


class DNSZoneRecordType(models.Model):
    """
    RR type
    """
    class Meta:
        verbose_name = _("DNS Zone Record Type")
        verbose_name_plural = _("DNS Zone Record Types")
        ordering = ["type"]
        db_table = "dns_dnszonerecordtype"
        app_label = "dns"

    type = models.CharField(_("Type"), max_length=16, unique=True)
    is_active = models.BooleanField(_("Is Active?"), default=True)
    validation = models.CharField(_("Validation"), max_length=256,
        blank=True, null=True,
        validators = [check_re],
        help_text=_("Regular expression to validate record. Following macros can be used: OCTET, IPv4, FQDN"))

    def __unicode__(self):
        return unicode(self.type)

    @classmethod
    def interpolate_re(cls, rx):
        """
        Replace macroses in regular expression. Following macroses are
        expanded:

        * OCTET - number in range 0 - 255
        * IPv4 - IPv4 address
        * FQDN - FQDN

        :param rx: Regular expression
        :type rx: str
        :return: Expanded regular expression
        :rtype: str
        """
        for m, s in [
            ("OCTET", r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"),
            ("IPv4", r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"),
            ("FQDN", r"([a-z0-9\-]+\.?)*")]:
            rx = rx.replace(m, s)
        return r"^%s$" % rx

    def is_valid(self, value):
        """
        Validate value conforms RR type
        """
        if self.validation:
            rx = DNSZoneRecordType.interpolate_re(self.validation)
            return re.match(rx, value) is not None
        else:
            return True

    def save(self):
        if self.validation:
            try:
                rx = DNSZoneRecordType.interpolate_re(self.validation)
            except:
                raise ValueError("Invalid regular expression: %s" % self.validation)
            try:
                re.compile(rx)
            except:
                raise ValueError("Invalid regular expression: %s" % rx)
        super(DNSZoneRecordType, self).save()
