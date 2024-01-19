# ---------------------------------------------------------------------
# Address model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from django.db import models
from django.contrib.postgres.fields import ArrayField

# NOC modules
from noc.config import config
from noc.core.model.decorator import on_init
from noc.core.model.base import NOCModel
from noc.project.models.project import Project
from noc.sa.models.managedobject import ManagedObject
from noc.core.model.fields import INETField, MACField
from noc.core.validators import ValidationError, check_fqdn, is_ipv4, is_ipv6
from noc.main.models.textindex import full_text_search
from noc.main.models.label import Label
from noc.main.models.remotesystem import RemoteSystem
from noc.core.model.fields import DocumentReferenceField
from noc.core.wf.decorator import workflow
from noc.wf.models.state import State
from noc.core.model.decorator import on_delete_check
from noc.core.bi.decorator import bi_sync
from noc.core.change.decorator import change
from noc.core.translation import ugettext as _
from .afi import AFI_CHOICES
from .vrf import VRF
from .addressprofile import AddressProfile


@Label.model
@on_init
@bi_sync
@change
@full_text_search
@workflow
@on_delete_check(check=[("ip.Address", "ipv6_transition")])
class Address(NOCModel):
    class Meta(object):
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        db_table = "ip_address"
        app_label = "ip"
        unique_together = [("vrf", "afi", "address")]

    prefix = models.ForeignKey("ip.Prefix", verbose_name=_("Prefix"), on_delete=models.CASCADE)
    vrf: "VRF" = models.ForeignKey(
        VRF, verbose_name=_("VRF"), default=VRF.get_global, on_delete=models.CASCADE
    )
    afi: str = models.CharField(_("Address Family"), max_length=1, choices=AFI_CHOICES)
    address: str = INETField(_("Address"))
    profile: "AddressProfile" = DocumentReferenceField(AddressProfile, null=False, blank=False)
    name: str = models.CharField(_("Name"), max_length=255, null=False, blank=False)
    fqdn: str = models.CharField(
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
    description: str = models.TextField(_("Description"), blank=True, null=True)
    # Labels
    labels = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(
        models.CharField(max_length=250), blank=True, null=True, default=list
    )
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
    # Last state change
    state_changed = models.DateTimeField("State Changed", null=True, blank=True)
    # Timestamp expired
    expired = models.DateTimeField("Expired", null=True, blank=True)
    # Timestamp of last seen
    last_seen = models.DateTimeField("Last Seen", null=True, blank=True)
    # Timestamp of first discovery
    first_discovered = models.DateTimeField("First Discovered", null=True, blank=True)
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem, null=True, blank=True)
    # Object id in remote system
    remote_id = models.CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = models.BigIntegerField(unique=True)

    csv_ignored_fields = ["prefix"]

    def __str__(self):
        return f"{self.vrf.name}({self.afi}): {self.address}"

    @classmethod
    def get_by_id(cls, id: int) -> Optional["Address"]:
        address = Address.objects.filter(id=id)[:1]
        if address:
            return address[0]
        return None

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_address:
            yield "address", self.id
        if config.datastream.enable_dnszone:
            from noc.dns.models.dnszone import DNSZone

            fqdn_changed, address_changed = [self.fqdn, changed_fields.get("fqdn")], [
                self.address,
                changed_fields.get("address"),
            ]
            for fqdn in fqdn_changed:
                if not fqdn:
                    continue
                # Touch forward zone
                fz = DNSZone.get_zone(fqdn)
                if fz:
                    for ds, dz_id in fz.iter_changed_datastream(changed_fields=changed_fields):
                        yield ds, dz_id
            for address in address_changed:
                if not address:
                    continue
                # Touch reverse zone
                rz = DNSZone.get_zone(address)
                if rz:
                    for ds, dz_id in rz.iter_changed_datastream(changed_fields=changed_fields):
                        yield ds, dz_id

    @classmethod
    def get_afi(cls, address: str) -> str:
        return "6" if ":" in address else "4"

    @classmethod
    def get_collision(cls, vrf: "VRF", address: str) -> Optional["Address"]:
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
        a = Address.objects.filter(
            afi=afi, address=address, vrf__in=vrf.vrf_group.vrf_set.exclude(id=vrf.id)
        ).first()
        if a:
            return a.vrf
        return None

    def save(self, *args, **kwargs):
        """
        Override default save() method to set AFI,
        parent prefix, and check VRF group restrictions
        :param kwargs:
        :return:
        """
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        """
        Field validation
        :return:
        """

        # Get proper AFI
        self.afi = "6" if ":" in self.address else "4"
        # Check prefix is of AFI type
        if self.is_ipv4 and not is_ipv4(self.address):
            raise ValidationError({"address": f"Invalid IPv4 {self.address}"})
        elif self.is_ipv6 and not is_ipv6(self.address):
            raise ValidationError({"address": f"Invalid IPv6 {self.address}"})
        # Check VRF
        if not self.vrf:
            self.vrf = VRF.get_global()
        # Find parent prefix
        self.prefix = Prefix.get_parent(self.vrf, self.afi, self.address)
        # Check VRF group restrictions
        cv = self.get_collision(self.vrf, self.address)
        if cv:
            # Collision detected
            raise ValidationError({"vrf": f"Address already exists in VRF {cv}"})

    @property
    def short_description(self) -> str:
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
        card = f"Address {self.address}, Name {self.name}"
        if self.fqdn:
            content += [self.fqdn]
            card += f", FQDN {self.fqdn}"
        if self.mac:
            content += [self.mac]
            card += f", MAC {self.mac}"
        if self.description:
            content += [self.description]
            card += f" ({self.description})"
        r = {
            "id": f"ip.address:{self.id}",
            "title": self.address,
            "content": "\n".join(content),
            "card": card,
        }
        if self.labels:
            r["tags"] = self.labels
        return r

    @classmethod
    def get_search_result_url(cls, obj_id) -> str:
        return f"/api/card/view/address/{obj_id}/"

    @property
    def is_ipv4(self) -> bool:
        return self.afi == "4"

    @property
    def is_ipv6(self) -> bool:
        return self.afi == "6"

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_ipaddress")


# Avoid django's validation failure
from .prefix import Prefix
