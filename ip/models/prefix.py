# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
=======
##----------------------------------------------------------------------
## Prefix model
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models, connection
from django.db.models import Q
from django.contrib.auth.models import User
## NOC modules
from noc.project.models.project import Project
from vrf import VRF
from afi import AFI_CHOICES
from noc.peer.models import AS
from noc.vc.models.vc import VC
from noc.main.models import Style, ResourceState
from noc.lib.fields import TagsField, CIDRField
from noc.lib.app import site
from noc.lib.validators import (check_ipv4_prefix, check_ipv6_prefix,
                                ValidationError)
from noc.lib.ip import IP, IPv4


>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
class Prefix(models.Model):
    """
    Allocated prefix
    """
<<<<<<< HEAD
    class Meta(object):
=======
    class Meta:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
    profile = DocumentReferenceField(
        PrefixProfile,
        null=False, blank=False
    )
    asn = models.ForeignKey(
        AS, verbose_name=_("AS"),
        help_text=_("Autonomous system granted with prefix"),
        null=True, blank=True
=======
    asn = models.ForeignKey(
        AS, verbose_name=_("AS"),
        help_text=_("Autonomous system granted with prefix"),
        default=AS.default_as
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
    state = DocumentReferenceField(
        State,
        null=True, blank=True
    )
=======
    style = models.ForeignKey(Style, verbose_name=_("Style"), blank=True,
                              null=True)
    state = models.ForeignKey(
        ResourceState,
        verbose_name=_("State"),
        default=ResourceState.get_default)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def __unicode__(self):
        return u"%s(%s): %s" % (self.vrf.name, self.afi, self.prefix)

<<<<<<< HEAD
    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        mo = Prefix.objects.filter(id=id)[:1]
        if mo:
            return mo[0]
        else:
            return None

=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def get_absolute_url(self):
        return site.reverse("ip:ipam:vrf_index", self.vrf.id, self.afi,
                            self.prefix)

    @property
    def has_transition(self):
        """
        Check prefix has ipv4/ipv6 transition
        :return:
        """
<<<<<<< HEAD
        if self.is_ipv4:
            return bool(self.ipv6_transition)
        else:
            try:
                # pylint: disable=pointless-statement
                self.ipv4_transition  # noqa
=======
        if self.afi == "4":
            return bool(self.ipv6_transition)
        else:
            try:
                self.ipv4_transition
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                return True
            except Prefix.DoesNotExist:
                return False

<<<<<<< HEAD
=======
    def clear_transition(self):
        if self.has_transition:
            if self.afi == "4":
                self.ipv6_transition = None
                self.save()
            else:
                self.ipv4_transition.ipv6_transition = None
                self.ipv4_transition.save()

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @classmethod
    def get_parent(cls, vrf, afi, prefix):
        """
        Get nearest closing prefix
        """
<<<<<<< HEAD
        r = list(
            Prefix.objects.raw("""
=======
        r = list(Prefix.objects.raw("""
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                SELECT id, prefix
                FROM ip_prefix
                WHERE
                        vrf_id=%s
                    AND afi=%s
                    AND prefix >> %s
                ORDER BY masklen(prefix) DESC
                LIMIT 1
<<<<<<< HEAD
            """, [vrf.id, str(afi), str(prefix)])
        )
=======
                """,
            [vrf.id, str(afi), str(prefix)]))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        if not r:
            return None
        return r[0]

    @property
<<<<<<< HEAD
    def is_ipv4(self):
        return self.afi == "4"

    @property
    def is_ipv6(self):
        return self.afi == "6"

    @property
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def is_root(self):
        """
        Returns true if the prefix is a root of VRF
        """
<<<<<<< HEAD
        return ((self.is_ipv4 and self.prefix == "0.0.0.0/0") or
                (self.is_ipv6 and self.prefix == "::/0"))
=======
        return (self.afi == "4" and self.prefix == "0.0.0.0/0") or (
        self.afi == "6" and self.prefix == "::/0")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def clean(self):
        """
        Field validation
        """
        super(Prefix, self).clean()
<<<<<<< HEAD
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
=======
        # Check prefix is of AFI type
        if self.afi == "4":
            check_ipv4_prefix(self.prefix)
        elif self.afi == "6":
            check_ipv6_prefix(self.prefix)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Check root prefix have no parent
        if self.is_root and self.parent:
            raise ValidationError("Root prefix cannot have parent")

    def save(self, **kwargs):
        """
        Save prefix
        """
<<<<<<< HEAD
        self.clean()
=======
        # Set defaults
        self.afi = "6" if ":" in self.prefix else "4"
        if not self.vrf:
            self.vrf = VRF.get_global()
        if not self.asn:
            self.asn = AS.default_as()
        if not self.is_root:
            # Set proper parent
            self.parent = Prefix.get_parent(
                self.vrf, self.afi, self.prefix)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        super(Prefix, self).save(**kwargs)
        # Rebuild tree if necessary
        # Reconnect children children prefixes
        c = connection.cursor()
<<<<<<< HEAD
        c.execute(
            """
=======
        c.execute("""
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            UPDATE %s
            SET    parent_id=%%s
            WHERE
                    vrf_id=%%s
                AND afi=%%s
                AND prefix << %%s
                AND parent_id=%%s
<<<<<<< HEAD
            """ % Prefix._meta.db_table,
            [
                self.id, self.vrf.id, self.afi, self.prefix,
                self.parent.id if self.parent else None
            ]
        )
        # Reconnect children addresses
        c.execute(
            """
=======
        """ % Prefix._meta.db_table,
            [self.id, self.vrf.id, self.afi, self.prefix,
             self.parent.id if self.parent else None]
        )
        # Reconnect children addresses
        c.execute("""
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            UPDATE %s
            SET prefix_id=%%s
            WHERE
                    prefix_id=%%s
                AND address << %%s
<<<<<<< HEAD
            """ % Address._meta.db_table,
=======
                """ % Address._meta.db_table,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
        if self.is_root and not getattr(self, "_disable_delete_protection", False):
=======
        if self.is_root:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            raise ValidationError("Cannot delete root prefix")
        # Reconnect children prefixes
        self.children_set.update(parent=self.parent)
        # Reconnect children addresses
        self.address_set.update(prefix=self.parent)
        # Unlink dual-stack allocations
<<<<<<< HEAD
        # self.clear_transition()
=======
        self.clear_transition()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Remove bookmarks
        self.prefixbookmark_set.all().delete()
        # Finally delete
        super(Prefix, self).delete(*args, **kwargs)

    def delete_recursive(self):
        """
        Delete prefix and all descendancies
        """
        # Unlink dual-stack allocations
<<<<<<< HEAD
        # self.clear_transition()
=======
        self.clear_transition()
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
        PrefixAccess.objects.filter(
            vrf=self.vrf,
            afi=self.afi
        ).extra(
=======
        PrefixAccess.objects.filter(vrf=self.vrf, afi=self.afi).extra(
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
        return User.objects.raw(
            """
=======
        return User.objects.raw("""
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
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
=======
            ORDER BY username""" % (
        User._meta.db_table, PrefixAccess._meta.db_table),
            [self.vrf.id, self.afi, self.prefix])

    ##
    ## First line of description
    ##
    @property
    def short_description(self):
        if self.description:
            return self.description.split("\n", 1)[0].strip()
        else:
            return ""

    ##
    ## Netmask for IPv4
    ##
    @property
    def netmask(self):
        if self.afi == "4":
            return IPv4(self.prefix).netmask.address
        else:
            return None

    ##
    ## Broadcast for IPv4
    ##
    @property
    def broadcast(self):
        if self.afi == "4":
            return IPv4(self.prefix).last.address
        else:
            return None

    ##
    ## Cisco wildcard for IPv4
    ##
    @property
    def wildcard(self):
        if self.afi == "4":
            return IPv4(self.prefix).wildcard.address
        else:
            return ""

    ##
    ## IPv4 prefix size
    ##
    @property
    def size(self):
        if self.afi == "4":
            return IPv4(self.prefix).size
        else:
            return None

    ##
    ## Return True if user has view access
    ##
    def can_view(self, user):
        return PrefixAccess.user_can_view(
            user, self.vrf, self.afi, self.prefix)

    ##
    ## Return True if user has change access
    ##
    def can_change(self, user):
        return PrefixAccess.user_can_change(
            user, self.vrf, self.afi, self.prefix)

    ##
    ## Check the user has bookmark on prefix
    ##
    def has_bookmark(self, user):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        try:
            PrefixBookmark.objects.get(user=user, prefix=self)
            return True
        except PrefixBookmark.DoesNotExist:
            return False

<<<<<<< HEAD
    def toggle_bookmark(self, user):
        """
        Toggle user bookmark. Returns new bookmark state
        :param user:
        :return:
        """
=======
    ##
    ## Toggle user bookmark. Returns new bookmark state
    ##
    def toggle_bookmark(self, user):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        b, created = PrefixBookmark.objects.get_or_create(user=user,
                                                          prefix=self)
        if created:
            return True
<<<<<<< HEAD
        b.delete()
        return False
=======
        else:
            b.delete()
            return False
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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

<<<<<<< HEAD
    def get_search_info(self, _user):
=======
    def get_search_info(self, user):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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

<<<<<<< HEAD
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
=======
    ##
    ## All prefix-related address ranges
    ##
    @property
    def address_ranges(self):
        return list(AddressRange.objects.raw("""
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
            [self.vrf.id, self.afi, self.prefix, self.prefix, self.prefix]))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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
<<<<<<< HEAD
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
=======
        b = IP.prefix(self.prefix)
        nb = IP.prefix(new_prefix)
        # Rebase prefix and all nested prefixes
        # Parents are left untouched
        for p in Prefix.objects.filter(vrf=self.vrf, afi=self.afi).extra(
            where=["prefix <<= %s"], params=[self.prefix]):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            np = IP.prefix(p.prefix).rebase(b, nb).prefix
            # Prefix.objects.filter(pk=p.pk).update(prefix=np, vrf=vrf)
            p.prefix = np
            p.vrf = vrf
            p.save()  # Raise events
        # Rebase addresses
        # Parents are left untouched
<<<<<<< HEAD
        for a in Address.objects.filter(
            vrf=self.vrf,
            afi=self.afi
        ).extra(
            where=["address <<= %s"],
            params=[self.prefix]
        ):
=======
        for a in Address.objects.filter(vrf=self.vrf, afi=self.afi).extra(
            where=["address <<= %s"], params=[self.prefix]):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            na = IP.prefix(a.address).rebase(b, nb).address
            # Address.objects.filter(pk=a.pk).update(address=na, vrf=vrf)
            a.address = na
            a.vrf = vrf
            a.save()  # Raise events
        # Rebase permissions
        # move all permissions to the nested blocks
<<<<<<< HEAD
        for pa in PrefixAccess.objects.filter(
            vrf=self.vrf
        ).extra(
            where=["prefix <<= %s"],
            params=[self.prefix]
        ):
=======
        for pa in PrefixAccess.objects.filter(vrf=self.vrf).extra(
            where=["prefix <<= %s"], params=[self.prefix]):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            np = IP.prefix(pa.prefix).rebase(b, nb).prefix
            PrefixAccess.objects.filter(pk=pa.pk).update(
                prefix=np, vrf=vrf)
        # create permissions for covered blocks
<<<<<<< HEAD
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
=======
        for pa in PrefixAccess.objects.filter(vrf=self.vrf).extra(
            where=["prefix >> %s"], params=[self.prefix]):
            PrefixAccess(user=pa.user, vrf=vrf, afi=pa.afi,
                prefix=new_prefix,  can_view=pa.can_view,
                can_change=pa.can_change).save()
        # @todo: Rebase bookmarks
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
            return "E"
        return self.enable_ip_discovery

    @property
    def usage(self):
        if self.is_ipv4:
=======
            else:
                return "E"
        else:
            return self.enable_ip_discovery

    @property
    def usage(self):
        if self.afi == "4":
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
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
=======
        else:
            return "%.2f%%" % u

# Avoid circular references
from address import Address
from prefixaccess import PrefixAccess
from prefixbookmark import PrefixBookmark
from addressrange import AddressRange
from ippool import IPPool
from noc.dns.models import DNSZone
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
