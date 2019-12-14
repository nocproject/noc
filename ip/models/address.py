# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Address model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# Third-party modules
import six
from noc.core.translation import ugettext as _
from django.db import models

# NOC modules
from noc.config import config
from noc.core.model.decorator import on_init
from noc.core.model.base import NOCModel
from noc.project.models.project import Project
from noc.sa.models.managedobject import ManagedObject
from noc.core.model.fields import TagsField, INETField, MACField
from noc.core.validators import ValidationError, check_fqdn, check_ipv4, check_ipv6
from noc.main.models.textindex import full_text_search
from noc.core.model.fields import DocumentReferenceField
from noc.core.wf.decorator import workflow
from noc.wf.models.state import State
from noc.core.model.decorator import on_delete_check
from noc.core.datastream.decorator import datastream
from .afi import AFI_CHOICES
from .vrf import VRF
from .addressprofile import AddressProfile


@on_init
@datastream
@full_text_search
@workflow
@on_delete_check(check=[("ip.Address", "ipv6_transition")])
@six.python_2_unicode_compatible
class Address(NOCModel):
    class Meta(object):
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        db_table = "ip_address"
        app_label = "ip"
        unique_together = [("vrf", "afi", "address")]

    prefix = models.ForeignKey("ip.Prefix", verbose_name=_("Prefix"), on_delete=models.CASCADE)
    vrf = models.ForeignKey(
        VRF, verbose_name=_("VRF"), default=VRF.get_global, on_delete=models.CASCADE
    )
    afi = models.CharField(_("Address Family"), max_length=1, choices=AFI_CHOICES)
    address = INETField(_("Address"))
    profile = DocumentReferenceField(AddressProfile, null=False, blank=False)
    name = models.CharField(_("Name"), max_length=255, null=False, blank=False)
    fqdn = models.CharField(
        _("FQDN"),
        max_length=255,
        help_text=_("Full-qualified Domain Name"),
        validators=[check_fqdn],
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        Project,
        verbose_name="Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="address_set",
    )
    mac = MACField("MAC", null=True, blank=True, help_text=_("MAC Address"))
    auto_update_mac = models.BooleanField(
        "Auto Update MAC", default=False, help_text=_("Set to auto-update MAC field")
    )
    managed_object = models.ForeignKey(
        ManagedObject,
        verbose_name=_("Managed Object"),
        null=True,
        blank=True,
        related_name="address_set",
        on_delete=models.SET_NULL,
        help_text=_("Set if address belongs to the Managed Object's interface"),
    )
    subinterface = models.CharField("SubInterface", max_length=128, null=True, blank=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    tags = TagsField(_("Tags"), null=True, blank=True)
    tt = models.IntegerField(_("TT"), blank=True, null=True, help_text=_("Ticket #"))
    state = DocumentReferenceField(State, null=True, blank=True)
    allocated_till = models.DateField(
        _("Allocated till"),
        null=True,
        blank=True,
        help_text=_("Address temporary allocated till the date"),
    )
    ipv6_transition = models.OneToOneField(
        "self",
        related_name="ipv4_transition",
        null=True,
        blank=True,
        limit_choices_to={"afi": "6"},
        on_delete=models.SET_NULL,
    )
    source = models.CharField(
        "Source",
        max_length=1,
        choices=[
            ("M", "Manual"),
            ("i", "Interface"),
            ("m", "Management"),
            ("d", "DHCP"),
            ("n", "Neighbor"),
        ],
        null=False,
        blank=False,
        default="M",
    )

    csv_ignored_fields = ["prefix"]

    def __str__(self):
        return "%s(%s): %s" % (self.vrf.name, self.afi, self.address)

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_address:
            yield "address", self.id
        if config.datastream.enable_dnszone:
            from noc.dns.models.dnszone import DNSZone

            if self.fqdn:
                # Touch forward zone
                fz = DNSZone.get_zone(self.fqdn)
                if fz:
                    for ds, id in fz.iter_changed_datastream(changed_fields=changed_fields):
                        yield ds, id
                # Touch reverse zone
                rz = DNSZone.get_zone(self.address)
                if rz:
                    for ds, id in rz.iter_changed_datastream(changed_fields=changed_fields):
                        yield ds, id

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
        if not vrf.vrf_group or vrf.vrf_group.address_constraint != "G":
            return None
        afi = cls.get_afi(address)
        try:
            a = Address.objects.get(
                afi=afi, address=address, vrf__in=vrf.vrf_group.vrf_set.exclude(id=vrf.id)
            )
            return a.vrf
        except Address.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        """
        Override default save() method to set AFI,
        parent prefix, and check VRF group restrictions
        :param kwargs:
        :return:
        """
        self.clean()
        super(Address, self).save(*args, **kwargs)

    def clean(self):
        """
        Field validation
        :return:
        """
        super(Address, self).clean()
        # Get proper AFI
        self.afi = "6" if ":" in self.address else "4"
        # Check prefix is of AFI type
        if self.is_ipv4:
            check_ipv4(self.address)
        elif self.is_ipv6:
            check_ipv6(self.address)
        # Check VRF
        if not self.vrf:
            self.vrf = VRF.get_global()
        # Find parent prefix
        self.prefix = Prefix.get_parent(self.vrf, self.afi, self.address)
        # Check VRF group restrictions
        cv = self.get_collision(self.vrf, self.address)
        if cv:
            # Collision detected
            raise ValidationError("Address already exists in VRF %s" % cv)

    @property
    def short_description(self):
        """
        First line of description
        """
        if self.description:
            return self.description.split("\n", 1)[0].strip()
        else:
            return ""

    def get_index(self):
        """
        Full-text search
        """
        content = [self.address, self.name]
        card = "Address %s, Name %s" % (self.address, self.name)
        if self.fqdn:
            content += [self.fqdn]
            card += ", FQDN %s" % self.fqdn
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
            "card": card,
        }
        if self.tags:
            r["tags"] = self.tags
        return r

    @classmethod
    def get_search_result_url(cls, obj_id):
        return "/api/card/view/address/%s/" % obj_id

    @property
    def is_ipv4(self):
        return self.afi == "4"

    @property
    def is_ipv6(self):
        return self.afi == "6"


# Avoid django's validation failure
from .prefix import Prefix
