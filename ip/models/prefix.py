# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Prefix model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import operator
from threading import Lock
# Third-party modules
from django.db import models, connection
from django.contrib.auth.models import User
import cachetools
# NOC modules
from noc.project.models.project import Project
from noc.peer.models.asn import AS
from noc.vc.models.vc import VC
from noc.core.model.fields import TagsField, CIDRField
from noc.lib.app.site import site
from noc.lib.validators import (check_ipv4_prefix, check_ipv6_prefix,
                                ValidationError)
from noc.core.model.fields import DocumentReferenceField
from noc.core.ip import IP, IPv4
from noc.main.models.textindex import full_text_search
from noc.core.translation import ugettext as _
from noc.core.wf.decorator import workflow
from noc.wf.models.state import State
from .vrf import VRF
from .afi import AFI_CHOICES
from .prefixprofile import PrefixProfile

id_lock = Lock()


@full_text_search
@workflow
class Prefix(models.Model):
    """
    Allocated prefix
    """
    class Meta(object):
        verbose_name = _("Prefix")
        verbose_name_plural = _("Prefixes")
        db_table = "ip_prefix"
        app_label = "ip"
        unique_together = [("vrf", "afi", "prefix")]

    parent = models.ForeignKey(
        "self",
        related_name="children_set",
        verbose_name=_("Parent"),
        null=True,
        blank=True)
    vrf = models.ForeignKey(
        VRF,
        verbose_name=_("VRF"),
        default=VRF.get_global
    )
    afi = models.CharField(
        _("Address Family"),
        max_length=1,
        choices=AFI_CHOICES)
    prefix = CIDRField(_("Prefix"))
    profile = DocumentReferenceField(
        PrefixProfile,
        null=False, blank=False
    )
    asn = models.ForeignKey(
        AS, verbose_name=_("AS"),
        help_text=_("Autonomous system granted with prefix"),
        null=True, blank=True
    )
    project = models.ForeignKey(
        Project, verbose_name="Project",
        on_delete=models.SET_NULL,
        null=True, blank=True, related_name="prefix_set")
    vc = models.ForeignKey(
        VC,
        verbose_name=_("VC"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_("VC bound to prefix"))
    description = models.TextField(
        _("Description"),
        blank=True,
        null=True)
    tags = TagsField("Tags", null=True, blank=True)
    tt = models.IntegerField(
        "TT",
        blank=True,
        null=True,
        help_text=_("Ticket #"))
    state = DocumentReferenceField(
        State,
        null=True, blank=True
    )
    allocated_till = models.DateField(
        _("Allocated till"),
        null=True,
        blank=True,
        help_text=_("Prefix temporary allocated till the date"))
    ipv6_transition = models.OneToOneField(
        "self",
        related_name="ipv4_transition",
        null=True, blank=True,
        limit_choices_to={"afi": "6"},
        on_delete=models.SET_NULL)
    enable_ip_discovery = models.CharField(
        _("Enable IP Discovery"),
        max_length=1,
        choices=[
            ("I", "Inherit"),
            ("E", "Enable"),
            ("D", "Disable")
        ],
        default="I",
        blank=False,
        null=False
    )

    csv_ignored_fields = ["parent"]
    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __unicode__(self):
        return u"%s(%s): %s" % (self.vrf.name, self.afi, self.prefix)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        mo = Prefix.objects.filter(id=id)[:1]
        if mo:
            return mo[0]
        else:
            return None

    def get_absolute_url(self):
        return site.reverse("ip:ipam:vrf_index", self.vrf.id, self.afi,
                            self.prefix)

    @property
    def has_transition(self):
        """
        Check prefix has ipv4/ipv6 transition
        :return:
        """
        if self.is_ipv4:
            return bool(self.ipv6_transition)
        else:
            try:
                # pylint: disable=pointless-statement
                self.ipv4_transition  # noqa
                return True
            except Prefix.DoesNotExist:
                return False

    @classmethod
    def get_parent(cls, vrf, afi, prefix):
        """
        Get nearest closing prefix
        """
        r = list(
            Prefix.objects.raw("""
                SELECT id, prefix
                FROM ip_prefix
                WHERE
                        vrf_id=%s
                    AND afi=%s
                    AND prefix >> %s
                ORDER BY masklen(prefix) DESC
                LIMIT 1
            """, [vrf.id, str(afi), str(prefix)])
        )
        if not r:
            return None
        return r[0]

    @property
    def is_ipv4(self):
        return self.afi == "4"

    @property
    def is_ipv6(self):
        return self.afi == "6"

    @property
    def is_root(self):
        """
        Returns true if the prefix is a root of VRF
        """
        return ((self.is_ipv4 and self.prefix == "0.0.0.0/0") or
                (self.is_ipv6 and self.prefix == "::/0"))

    def clean(self):
        """
        Field validation
        """
        super(Prefix, self).clean()
        # Set defaults
        self.afi = "6" if ":" in self.prefix else "4"
        # Check prefix is of AFI type
        if self.is_ipv4:
            check_ipv4_prefix(self.prefix)
        elif self.is_ipv6:
            check_ipv6_prefix(self.prefix)
        # Set defaults
        if not self.vrf:
            self.vrf = VRF.get_global()
        if not self.asn:
            self.asn = AS.default_as()
        if not self.is_root:
            # Set proper parent
            self.parent = Prefix.get_parent(self.vrf, self.afi, self.prefix)
        # Check root prefix have no parent
        if self.is_root and self.parent:
            raise ValidationError("Root prefix cannot have parent")

    def save(self, **kwargs):
        """
        Save prefix
        """
        self.clean()
        super(Prefix, self).save(**kwargs)
        # Rebuild tree if necessary
        # Reconnect children children prefixes
        c = connection.cursor()
        c.execute(
            """
            UPDATE %s
            SET    parent_id=%%s
            WHERE
                    vrf_id=%%s
                AND afi=%%s
                AND prefix << %%s
                AND parent_id=%%s
            """ % Prefix._meta.db_table,
            [
                self.id, self.vrf.id, self.afi, self.prefix,
                self.parent.id if self.parent else None
            ]
        )
        # Reconnect children addresses
        c.execute(
            """
            UPDATE %s
            SET prefix_id=%%s
            WHERE
                    prefix_id=%%s
                AND address << %%s
            """ % Address._meta.db_table,
            [
                self.id,
                self.parent.id if self.parent else None,
                self.prefix
            ]
        )

    def delete(self, *args, **kwargs):
        """
        Delete prefix
        """
        if self.is_root and not getattr(self, "_disable_delete_protection", False):
            raise ValidationError("Cannot delete root prefix")
        # Reconnect children prefixes
        self.children_set.update(parent=self.parent)
        # Reconnect children addresses
        self.address_set.update(prefix=self.parent)
        # Unlink dual-stack allocations
        # self.clear_transition()
        # Remove bookmarks
        self.prefixbookmark_set.all().delete()
        # Finally delete
        super(Prefix, self).delete(*args, **kwargs)

    def delete_recursive(self):
        """
        Delete prefix and all descendancies
        """
        # Unlink dual-stack allocations
        # self.clear_transition()
        # Recursive delete
        # Get nested prefixes
        ids = Prefix.objects.filter(
            vrf=self.vrf,
            afi=self.afi
        ).extra(
            where=["prefix <<= %s"],
            params=[self.prefix]
        ).values_list("id", flat=True)
        #
        zones = set()
        for a in Address.objects.filter(prefix__in=ids):
            zones.add(a.address)
            zones.add(a.fqdn)
        # Delete nested addresses
        Address.objects.filter(prefix__in=ids).delete()
        # Delete nested prefixes
        Prefix.objects.filter(id__in=ids).delete()
        # Delete permissions
        PrefixAccess.objects.filter(
            vrf=self.vrf,
            afi=self.afi
        ).extra(
            where=["prefix <<= %s"],
            params=[self.prefix]
        )
        # Touch dns zones
        for z in zones:
            DNSZone.touch(z)

    @property
    def maintainers(self):
        """
        List of persons having write access
        @todo: PostgreSQL-independent implementation
        """
        return User.objects.raw(
            """
            SELECT id,username,first_name,last_name
            FROM %s u
            WHERE
                is_active=TRUE
                AND
                    (is_superuser=TRUE
                    OR
                    EXISTS(SELECT id
                           FROM %s a
                           WHERE
                                    user_id=u.id
                                AND vrf_id=%%s
                                AND afi=%%s
                                AND prefix>>=%%s
                                AND can_change=TRUE
                           ))
            ORDER BY username
            """ % (User._meta.db_table, PrefixAccess._meta.db_table),
            [
                self.vrf.id, self.afi, self.prefix
            ]
        )

    @property
    def short_description(self):
        """
        Returns first line of description
        :return:
        """
        if self.description:
            return self.description.split("\n", 1)[0].strip()
        return ""

    @property
    def netmask(self):
        """
        returns Netmask for IPv4
        :return:
        """
        if self.is_ipv4:
            return IPv4(self.prefix).netmask.address
        return None

    @property
    def broadcast(self):
        """
        Returns Broadcast for IPv4
        :return:
        """
        if self.is_ipv4:
            return IPv4(self.prefix).last.address
        return None

    @property
    def wildcard(self):
        """
        Returns Cisco wildcard for IPv4
        :return:
        """
        if self.is_ipv4:
            return IPv4(self.prefix).wildcard.address
        return ""

    @property
    def size(self):
        """
        Returns IPv4 prefix size
        :return:
        """
        if self.is_ipv4:
            return IPv4(self.prefix).size
        return None

    def can_view(self, user):
        """
        Returns True if user has view access
        :param user:
        :return:
        """
        return PrefixAccess.user_can_view(
            user, self.vrf, self.afi, self.prefix)

    def can_change(self, user):
        """
        Returns True if user has change access
        :param user:
        :return:
        """
        return PrefixAccess.user_can_change(
            user, self.vrf, self.afi, self.prefix)

    def has_bookmark(self, user):
        """
        Check the user has bookmark on prefix
        :param user:
        :return:
        """
        try:
            PrefixBookmark.objects.get(user=user, prefix=self)
            return True
        except PrefixBookmark.DoesNotExist:
            return False

    def toggle_bookmark(self, user):
        """
        Toggle user bookmark. Returns new bookmark state
        :param user:
        :return:
        """
        b, created = PrefixBookmark.objects.get_or_create(user=user,
                                                          prefix=self)
        if created:
            return True
        b.delete()
        return False

    def get_index(self):
        """
        Full-text search
        """
        content = [self.prefix]
        card = "Prefix %s" % self.prefix
        if self.description:
            content += [self.description]
            card += " (%s)" % self.description
        r = {
            "id": "ip.prefix:%s" % self.id,
            "title": self.prefix,
            "content": "\n".join(content),
            "card": card
        }
        if self.tags:
            r["tags"] = self.tags
        return r

    def get_search_info(self, _user):
        # @todo: Check user access
        return (
            "iframe",
            None,
            {
                "title": "Assigned addresses",
                "url": "/ip/ipam/%s/%s/%s/" % (
                    self.vrf.id, self.afi, self.prefix
                )
            }
        )

    @property
    def address_ranges(self):
        """
        All prefix-related address ranges
        :return:
        """
        return list(
            AddressRange.objects.raw(
                """
                SELECT *
                FROM ip_addressrange
                WHERE
                        vrf_id=%s
                    AND afi=%s
                    AND is_active=TRUE
                    AND
                        (
                                from_address << %s
                            OR  to_address << %s
                            OR  %s BETWEEN from_address AND to_address
                        )
                ORDER BY from_address, to_address
                """,
                [
                    self.vrf.id, self.afi,
                    self.prefix,
                    self.prefix, self.prefix
                ]
            )
        )

    @property
    def ippools(self):
        """
        All nested IP Pools
        """
        return list(IPPool.objects.raw("""
            SELECT *
            FROM ip_ippool i
            WHERE
                  vrf_id = %s
              AND afi = %s
              AND from_address << %s
              AND to_address << %s
              AND NOT EXISTS (
                SELECT id
                FROM ip_prefix p
                WHERE
                      vrf_id = i.vrf_id
                  AND afi = i.afi
                  AND prefix << %s
                  AND
                    (
                      from_address << p.prefix
                      OR to_address << p.prefix
                    )
              )
            ORDER BY from_address
        """, [self.vrf.id, self.afi, self.prefix, self.prefix, self.prefix]))

    def rebase(self, vrf, new_prefix):
        """
        Rebase prefix to a new location
        :param vrf:
        :param new_prefix:
        :return:
        """
        #
        b = IP.prefix(self.prefix)
        nb = IP.prefix(new_prefix)
        # Validation
        if vrf == self.vrf and self.prefix == new_prefix:
            raise ValueError("Cannot rebase to self")
        if b.afi != nb.afi:
            raise ValueError("Cannot change address family during rebase")
        if b.mask < nb.mask:
            raise ValueError("Cannot rebase to prefix of lesser size")
        # Rebase prefix and all nested prefixes
        # Parents are left untouched
        for p in Prefix.objects.filter(
            vrf=self.vrf,
            afi=self.afi
        ).extra(
            where=["prefix <<= %s"],
            params=[self.prefix]
        ):
            np = IP.prefix(p.prefix).rebase(b, nb).prefix
            # Prefix.objects.filter(pk=p.pk).update(prefix=np, vrf=vrf)
            p.prefix = np
            p.vrf = vrf
            p.save()  # Raise events
        # Rebase addresses
        # Parents are left untouched
        for a in Address.objects.filter(
            vrf=self.vrf,
            afi=self.afi
        ).extra(
            where=["address <<= %s"],
            params=[self.prefix]
        ):
            na = IP.prefix(a.address).rebase(b, nb).address
            # Address.objects.filter(pk=a.pk).update(address=na, vrf=vrf)
            a.address = na
            a.vrf = vrf
            a.save()  # Raise events
        # Rebase permissions
        # move all permissions to the nested blocks
        for pa in PrefixAccess.objects.filter(
            vrf=self.vrf
        ).extra(
            where=["prefix <<= %s"],
            params=[self.prefix]
        ):
            np = IP.prefix(pa.prefix).rebase(b, nb).prefix
            PrefixAccess.objects.filter(pk=pa.pk).update(
                prefix=np, vrf=vrf)
        # create permissions for covered blocks
        for pa in PrefixAccess.objects.filter(
            vrf=self.vrf
        ).extra(
            where=["prefix >> %s"],
            params=[self.prefix]
        ):
            PrefixAccess(
                user=pa.user,
                vrf=vrf,
                afi=pa.afi,
                prefix=new_prefix,
                can_view=pa.can_view,
                can_change=pa.can_change
            ).save()
        # @todo: Rebase bookmarks
        # @todo: Update caches
        # Return rebased prefix
        return Prefix.objects.get(pk=self.pk)  # Updated object

    @property
    def nested_prefix_set(self):
        """
        Queryset returning all nested prefixes inside the prefix
        """
        return Prefix.objects.filter(vrf=self.vrf, afi=self.afi).extra(
            where=["prefix <<= %s"], params=[self.prefix])

    @property
    def nested_address_set(self):
        """
        Queryset returning all nested addresses inside the prefix
        """
        return Address.objects.filter(vrf=self.vrf, afi=self.afi).extra(
            where=["address <<= %s"], params=[self.prefix])

    def iter_free(self):
        """
        Generator returning all available free prefixes inside
        :return:
        """
        for fp in IP.prefix(self.prefix).iter_free(
                [p.prefix for p in self.children_set.all()]):
            yield str(fp)

    @property
    def effective_ip_discovery(self):
        if self.enable_ip_discovery == "I":
            if self.parent:
                return self.parent.effective_ip_discovery
            return "E"
        return self.enable_ip_discovery

    @property
    def usage(self):
        if self.is_ipv4:
            size = IPv4(self.prefix).size
            if not size:
                return 100.0
            n_ips = Address.objects.filter(prefix=self).count()
            n_pfx = sum(
                IPv4(p).size
                for p in Prefix.objects.filter(parent=self).only("prefix").values_list("prefix", flat=True)
            )
            if n_ips:
                if size > 2:  # Not /31 or /32
                    size -= 2  # Exclude broadcast and network
            return float(n_ips + n_pfx) * 100.0 / float(size)
        else:
            return None

    @property
    def usage_percent(self):
        u = self.usage
        if u is None:
            return ""
        return "%.2f%%" % u

    def is_empty(self):
        """
        Check prefix is empty and does not contain nested prefixes
        and addresses
        :return:
        """
        if Prefix.objects.filter(parent=self).count() > 0:
            return False
        if Address.objects.filter(prefix=self).count() > 0:
            return False
        return True

    def disable_delete_protection(self):
        """
        Disable root delete protection
        :return:
        """
        self._disable_delete_protection = True


# Avoid circular references
from noc.dns.models.dnszone import DNSZone
from .address import Address
from .prefixaccess import PrefixAccess
from .prefixbookmark import PrefixBookmark
from .addressrange import AddressRange
from .ippool import IPPool
