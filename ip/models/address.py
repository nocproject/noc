# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Address model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
## NOC modules
from noc.project.models.project import Project
from vrf import VRF
from prefix import Prefix
from afi import AFI_CHOICES
from noc.main.models import Style, ResourceState
from noc.sa.models import ManagedObject
from noc.lib.fields import TagsField, INETField, MACField
from noc.lib.app import site
from noc.lib.validators import (
    ValidationError, check_fqdn, check_ipv4, check_ipv6)


class Address(models.Model):
    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        db_table = "ip_address"
        app_label = "ip"
        unique_together = [("vrf", "afi", "address")]

    prefix = models.ForeignKey(Prefix, verbose_name=_("Prefix"))
    vrf = models.ForeignKey(
        VRF,
        verbose_name=_("VRF"),
        default=VRF.get_global
    )
    afi = models.CharField(
        _("Address Family"),
        max_length=1,
        choices=AFI_CHOICES)
    address = INETField(_("Address"))
    fqdn = models.CharField(
        _("FQDN"),
        max_length=255,
        help_text=_("Full-qualified Domain Name"),
        validators=[check_fqdn])
    project = models.ForeignKey(
        Project, verbose_name="Project",
        null=True, blank=True, related_name="address_set")
    mac = MACField(
        "MAC",
        null=True,
        blank=True,
        help_text=_("MAC Address"))
    auto_update_mac = models.BooleanField(
        "Auto Update MAC",
        default=False,
        help_text=_("Set to auto-update MAC field"))
    managed_object = models.ForeignKey(
        ManagedObject,
        verbose_name=_("Managed Object"),
        null=True, blank=True,
        related_name="address_set",
        on_delete=models.SET_NULL,
        help_text=_("Set if address belongs to the Managed Object's interface"))
    description = models.TextField(
        _("Description"),
        blank=True, null=True)
    tags = TagsField(_("Tags"), null=True, blank=True)
    tt = models.IntegerField(
        _("TT"),
        blank=True, null=True,
        help_text=_("Ticket #"))
    style = models.ForeignKey(
        Style,
        verbose_name=_("Style"),
        blank=True, null=True)
    state = models.ForeignKey(
        ResourceState,
        verbose_name=_("State"),
        default=ResourceState.get_default)
    allocated_till = models.DateField(
        _("Allocated till"),
        null=True, blank=True,
        help_text=_("Address temporary allocated till the date"))
    ipv6_transition = models.OneToOneField(
        "self",
        related_name="ipv4_transition",
        null=True, blank=True,
        limit_choices_to={"afi": "6"},
        on_delete=models.SET_NULL)

    csv_ignored_fields = ["prefix"]

    def __unicode__(self):
        return u"%s(%s): %s" % (self.vrf.name, self.afi, self.address)

    def get_absolute_url(self):
        return site.reverse("ip:ipam:vrf_index", self.vrf.id, self.afi,
                            self.prefix.prefix)

    @classmethod
    def get_afi(cls, address):
        return "6" if ":" in address else "4"

    @classmethod
    def get_collision(cls, vrf, address):
        """
        Check VRFGroup restrictions
        :param vrf:
        :param address:
        :return: VRF already containing address or None
        :rtype: VRF or None
        """
        if vrf.vrf_group.address_constraint != "G":
            return None
        afi = cls.get_afi(address)
        try:
            a = Address.objects.get(afi=afi, address=address,
                vrf__in=vrf.vrf_group.vrf_set.exclude(id=vrf.id))
            return a.vrf
        except Address.DoesNotExist:
            return None

    def save(self, **kwargs):
        """
        Override default save() method to set AFI,
        parent prefix, and check VRF group restrictions
        :param kwargs:
        :return:
        """
        # Check VRF group restrictions
        cv = self.get_collision(self.vrf, self.address)
        if cv:
            # Collision detected
            raise ValidationError("Address already exists in VRF %s" % cv)
        # Detect AFI
        self.afi = self.get_afi(self.address)
        # Set proper prefix
        self.prefix = Prefix.get_parent(self.vrf, self.afi, self.address)
        old = None
        if self.pk:
            old = Address.objects.get(pk=self.pk)
        super(Address, self).save(**kwargs)
        # If address or fqdn changed, touch zones
        if (not old or self.address != old.address or
            self.fqdn != old.fqdn or self.vrf != old.vrf):
            # Touch reverse zone
            DNSZone.touch(self.address)
            # Touch forward zone
            DNSZone.touch(self.fqdn)
            if old and old.fqdn and old.fqdn != self.fqdn:
                # Touch old forward zone too
                DNSZone.touch(old.fqdn)

    def delete(self):
        fqdn = self.fqdn
        address = self.address
        super(Address, self).delete()
        DNSZone.touch(fqdn)
        DNSZone.touch(address)

    def clean(self):
        """
        Field validation
        :return:
        """
        self.prefix = Prefix.get_parent(self.vrf, self.afi, self.address)
        super(Address, self).clean()
        # Check prefix is of AFI type
        if self.afi == "4":
            check_ipv4(self.address)
        elif self.afi == "6":
            check_ipv6(self.address)

    ##
    ## First line of description
    ##
    @property
    def short_description(self):
        if self.description:
            return self.description.split("\n", 1)[0].strip()
        else:
            return ""

    def get_index(self):
        """
        Full-text search
        """
        content = [self.address, self.fqdn]
        card = "Address %s, FQDN %s" % (self.address, self.fqdn)
        if self.mac:
            content += [self.mac]
            card += ", MAC %s" % self.mac
        if self.description:
            content += [self.description]
            card += " (%s)" % self.description
        r = {
            "id": "ip.address:%s" % self.id,
            "title": self.address,
            "content": "\n".join(content),
            "card": card
        }
        if self.tags:
            r["tags"] = self.tags
        return r

    def get_search_info(self, user):
        # @todo: Check user access
        return (
            "iframe",
            None,
            {
                "title": "Assigned addresses",
                "url": "/ip/ipam/%s/%s/%s/change_address/" % (
                    self.vrf.id, self.afi, self.address
                )
            }
        )

## Prevent import loop
from noc.dns.models import DNSZone
