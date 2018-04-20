# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# AddressRange model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# Third-party modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.template import Template, Context
# NOC modules
from noc.core.model.fields import TagsField, CIDRField
from noc.lib.app.site import site
from noc.core.ip import IP
from noc.lib.validators import check_ipv4, check_ipv6
from .afi import AFI_CHOICES
from .vrf import VRF
from .address import Address


class AddressRange(models.Model):
    class Meta(object):
        verbose_name = _("Address Range")
=======
##----------------------------------------------------------------------
## AddressRange model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.template import Template, Context
## NOC modules
from vrf import VRF
from address import Address
from afi import AFI_CHOICES
from noc.lib.fields import TagsField, CIDRField
from noc.lib.app import site
from noc.lib.ip import IP
from noc.lib.validators import check_ipv4, check_ipv6


class AddressRange(models.Model):
    class Meta:
        verbose_name = _("Address Range")
        verbose_name = _("Address Ranges")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        db_table = "ip_addressrange"
        app_label = "ip"
        unique_together = [("vrf", "afi", "from_address", "to_address")]

    name = models.CharField(_("Name"), max_length=64, unique=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    vrf = models.ForeignKey(VRF, verbose_name=_("VRF"))
    afi = models.CharField(
        _("Address Family"),
        max_length=1,
        choices=AFI_CHOICES)
    from_address = CIDRField(_("From Address"))
    to_address = CIDRField(_("To address"))
    description = models.TextField(_("Description"), blank=True, null=True)
    is_locked = models.BooleanField(
        _("Is Locked"),
        default=False,
        help_text=_("Check to deny address creation or editing within the range"))
    action = models.CharField(
        _("Action"),
        max_length=1,
        choices=[
            ("N", _("Do nothing")),
            ("G", _("Generate FQDNs")),
            ("D", _("Partial reverse zone delegation"))
        ],
        default="N")
    fqdn_template = models.CharField(
        _("FQDN Template"),
        max_length=255,
        null=True, blank=True,
        help_text=_("Template to generate FQDNs when 'Action' set to 'Generate FQDNs'"))
    reverse_nses = models.CharField(
        _("Reverse NSes"),
        max_length=255,
        null=True, blank=True,
        help_text=_("Comma-separated list of NSes to partial reverse zone delegation when 'Action' set to 'Partial reverse zone delegation"))
    tags = TagsField(_("Tags"), null=True, blank=True)
    tt = models.IntegerField(
        "TT",
        blank=True, null=True,
        help_text=_("Ticket #"))
    allocated_till = models.DateField(
        _("Allocated till"),
        null=True, blank=True,
        help_text=_("VRF temporary allocated till the date"))

    def __unicode__(self):
        return u"%s (IPv%s): %s -- %s" % (
<<<<<<< HEAD
            self.vrf.name,
            self.afi,
            self.from_address,
            self.to_address
        )
=======
        self.vrf.name, self.afi, self.from_address, self.to_address)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def clean(self):
        """
        Field validation
        """
        super(AddressRange, self).clean()
        # Check prefix is of AFI type
        if self.afi == "4":
            check_ipv4(self.from_address)
            check_ipv4(self.to_address)
        elif self.afi == "6":
            check_ipv6(self.from_address)
            check_ipv6(self.to_address)

    def get_absolute_url(self):
        return site.reverse("ip:addressrange:change", self.id)

<<<<<<< HEAD
=======
    ##
    ## Save instance
    ##
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def save(self, **kwargs):
        def generate_fqdns():
            # Prepare FQDN template
            t = Template(self.fqdn_template)
            # Sync FQDNs
            sn = 0
            for ip in self.addresses:
                # Generage FQDN
                vars = {
                    "afi": self.afi,
                    "vrf": self.vrf,
                    "range": self,
                    "n": sn
                }
                sn += 1
                if self.afi == "4":
                    i = ip.address.split(".")
                    vars["ip"] = i  # ip.0 .. ip.3
                    # ip1, ip2, ip3, ip4 for backward compatibility
                    for n, i in enumerate(i):
                        vars["ip%d" % (n + 1)] = i
                elif self.afi == "6":
                    vars["ip"] = ip.digits  # ip.0 .. ip.31
                fqdn = t.render(Context(vars))
                description = "Generated by address range '%s'" % self.name
                # Create or update address record when necessary
                a, created = Address.objects.get_or_create(
                    vrf=self.vrf, afi=self.afi, address=ip.address)
                if created:
                    a.fqdn = fqdn
                    a.description = description
                    a.save()
                elif a.fqdn != fqdn or a.description != a.description:
                    a.fqdn = fqdn
                    a.description = description
                    a.save()

        created = self.id is None
        if not created:
            # Get old values
            old = AddressRange.objects.get(id=self.id)
        super(AddressRange, self).save(**kwargs)
        if created:
            # New
            if self.action == "G":
                generate_fqdns()
        else:
            # Changed
            if old.action == "G" and self.action != "G":
                # Drop all auto-generated IPs
                Address.objects.filter(vrf=self.vrf, afi=self.afi,
                                       address__gte=self.from_address,
                                       address__lte=self.to_address).delete()
            elif old.action != "G" and self.action == "G":
                # Generate IPs
                generate_fqdns()
            elif self.action == "G":
                # Check for boundaries change
                if IP.prefix(old.from_address) < IP.prefix(self.from_address):
                    # Lower boundary raised up. Clean up addresses falled out of range
                    Address.objects.filter(
                        vrf=self.vrf, afi=self.afi,
                        address__gte=old.from_address,
                        address__lt=self.to_address).delete()
                if IP.prefix(old.to_address) > IP.prefix(self.to_address):
                    # Upper boundary is lowered. Clean up addressess falled out of range
                    Address.objects.filter(
<<<<<<< HEAD
                        vrf=self.vrf,
                        afi=self.afi,
                        address__gt=self.to_address,
                        address__lte=old.to_address
                    ).delete()
=======
                        vrf=self.vrf, afi=self.afi,
                                           address__gt=self.to_address,
                                           address__lte=old.to_address).delete()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    # Finally recheck FQDNs
                generate_fqdns()

    @property
    def short_description(self):
        """
        First line of description
        """
        if self.description:
            return self.description.split("\n", 1)[0].strip()
        else:
            return ""

    @property
    def addresses(self):
        """
        Generator returning all addresses in range
        """
        return IP.prefix(self.from_address).iter_address(
            until=IP.prefix(self.to_address))

<<<<<<< HEAD
    @classmethod
    def get_overlapping_ranges(cls, vrf, afi, from_address, to_address):
        """
        Returns a list of overlapping ranges
        :param vrf:
        :param afi:
        :param from_address:
        :param to_address:
        :return:
        """
=======
    ##
    ## Returns a list of overlapping ranges
    ##
    @classmethod
    def get_overlapping_ranges(cls, vrf, afi, from_address, to_address):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return AddressRange.objects.raw("""
            SELECT *
            FROM ip_addressrange
            WHERE
                    vrf_id=%(vrf)s
                AND afi=%(afi)s
                AND is_active
                AND (
                        from_address BETWEEN %(from_address)s AND %(to_address)s
                    OR  to_address BETWEEN %(from_address)s AND %(to_address)s
                    OR  %(from_address)s BETWEEN from_address AND to_address
                    OR  %(to_address)s BETWEEN from_address AND to_address
                )
        """, {
            "vrf": vrf.id,
            "afi": afi,
            "from_address": from_address,
            "to_address": to_address
        })

<<<<<<< HEAD
    @property
    def overlapping_ranges(self):
        """
        Returns a queryset with overlapped ranges
        :return:
        """
=======
    ##
    ## Returns a queryset with overlapped ranges
    ##
    @property
    def overlapping_ranges(self):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return self.get_overlapping_ranges(
            self.vrf, self.afi, self.from_address, self.to_address)

    @classmethod
    def address_is_locked(cls, vrf, afi, address):
        """
        Check wrether address is locked by any range
        """
        return AddressRange.objects.filter(
            vrf=vrf, afi=afi, is_locked=True,
            is_active=True,
            from_address__lte=address,
            to_address__gte=address).exists()
