# ---------------------------------------------------------------------
# AddressRange model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from noc.core.translation import ugettext as _
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.template import Template, Context

# NOC modules
from noc.core.model.base import NOCModel
from noc.config import config
from noc.core.model.fields import CIDRField
from noc.core.ip import IP
from noc.core.validators import check_ipv4, check_ipv6
from noc.core.change.decorator import change
from noc.main.models.label import Label
from .afi import AFI_CHOICES
from .vrf import VRF


@Label.model
@change
class AddressRange(NOCModel):
    class Meta(object):
        verbose_name = _("Address Range")
        db_table = "ip_addressrange"
        app_label = "ip"
        unique_together = [("vrf", "afi", "from_address", "to_address")]

    name = models.CharField(_("Name"), max_length=64, unique=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    vrf = models.ForeignKey(VRF, verbose_name=_("VRF"), on_delete=models.CASCADE)
    afi = models.CharField(_("Address Family"), max_length=1, choices=AFI_CHOICES)
    from_address = CIDRField(_("From Address"))
    to_address = CIDRField(_("To address"))
    description = models.TextField(_("Description"), blank=True, null=True)
    is_locked = models.BooleanField(
        _("Is Locked"),
        default=False,
        help_text=_("Check to deny address creation or editing within the range"),
    )
    action = models.CharField(
        _("Action"),
        max_length=1,
        choices=[
            ("N", _("Do nothing")),
            ("G", _("Generate FQDNs")),
            ("D", _("Partial reverse zone delegation")),
        ],
        default="N",
    )
    fqdn_template = models.CharField(
        _("FQDN Template"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_("Template to generate FQDNs when 'Action' set to 'Generate FQDNs'"),
    )
    reverse_nses = models.CharField(
        _("Reverse NSes"),
        max_length=255,
        null=True,
        blank=True,
        help_text=_(
            "Comma-separated list of NSes to partial reverse zone delegation when "
            "'Action' set to 'Partial reverse zone delegation"
        ),
    )
    # Labels
    labels = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list)
    effective_labels = ArrayField(
        models.CharField(max_length=250), blank=True, null=True, default=list
    )
    tt = models.IntegerField("TT", blank=True, null=True, help_text=_("Ticket #"))
    allocated_till = models.DateField(
        _("Allocated till"),
        null=True,
        blank=True,
        help_text=_("VRF temporary allocated till the date"),
    )

    def __str__(self):
        return "%s (IPv%s): %s -- %s" % (
            self.vrf.name,
            self.afi,
            self.from_address,
            self.to_address,
        )

    @classmethod
    def get_by_id(cls, id: int) -> Optional["AddressRange"]:
        addressrange = AddressRange.objects.filter(id=id)[:1]
        if addressrange:
            return addressrange[0]
        return None

    def iter_changed_datastream(self, changed_fields=None):
        if not config.datastream.enable_dnszone:
            return

        from noc.dns.models.dnszone import DNSZone

        if self.action == "D":
            zone = DNSZone.get_reverse_for_address(self.from_address)
            if zone:
                yield "dnszone", zone.id

    def clean(self):
        """
        Field validation
        """
        super().clean()
        # Check prefix is of AFI type
        if self.afi == "4":
            check_ipv4(self.from_address)
            check_ipv4(self.to_address)
        elif self.afi == "6":
            check_ipv6(self.from_address)
            check_ipv6(self.to_address)

    def save(self, *args, **kwargs):
        def generate_fqdns():
            # Prepare FQDN template
            t = Template(self.fqdn_template)
            # Sync FQDNs
            sn = 0
            for ip in self.addresses:
                # Generage FQDN
                vars = {"afi": self.afi, "vrf": self.vrf, "range": self, "n": sn}
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
                    vrf=self.vrf, afi=self.afi, address=ip.address
                )
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
        super().save(*args, **kwargs)
        if created:
            # New
            if self.action == "G":
                generate_fqdns()
        else:
            # Changed
            if old.action == "G" and self.action != "G":
                # Drop all auto-generated IPs
                Address.objects.filter(
                    vrf=self.vrf,
                    afi=self.afi,
                    address__gte=self.from_address,
                    address__lte=self.to_address,
                ).delete()
            elif old.action != "G" and self.action == "G":
                # Generate IPs
                generate_fqdns()
            elif self.action == "G":
                # Check for boundaries change
                if IP.prefix(old.from_address) < IP.prefix(self.from_address):
                    # Lower boundary raised up. Clean up addresses falled out of range
                    Address.objects.filter(
                        vrf=self.vrf,
                        afi=self.afi,
                        address__gte=old.from_address,
                        address__lt=self.to_address,
                    ).delete()
                if IP.prefix(old.to_address) > IP.prefix(self.to_address):
                    # Upper boundary is lowered. Clean up addressess falled out of range
                    Address.objects.filter(
                        vrf=self.vrf,
                        afi=self.afi,
                        address__gt=self.to_address,
                        address__lte=old.to_address,
                    ).delete()
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
        return IP.prefix(self.from_address).iter_address(until=IP.prefix(self.to_address))

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
        return AddressRange.objects.raw(
            """
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
        """,
            {"vrf": vrf.id, "afi": afi, "from_address": from_address, "to_address": to_address},
        )

    @property
    def overlapping_ranges(self):
        """
        Returns a queryset with overlapped ranges
        :return:
        """
        return self.get_overlapping_ranges(self.vrf, self.afi, self.from_address, self.to_address)

    @classmethod
    def address_is_locked(cls, vrf, afi, address):
        """
        Check wrether address is locked by any range
        """
        return AddressRange.objects.filter(
            vrf=vrf,
            afi=afi,
            is_locked=True,
            is_active=True,
            from_address__lte=address,
            to_address__gte=address,
        ).exists()

    @classmethod
    def can_set_label(cls, label):
        return Label.get_effective_setting(label, setting="enable_ipaddressrange")


# Avoid circular references
from .address import Address
