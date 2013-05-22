# -*- coding: utf-8 -*-
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
from noc.main.models import Style, ResourceState, CustomField
from noc.lib.fields import TagsField, CIDRField
from noc.lib.app import site
from noc.lib.search import SearchResult
from noc.lib.validators import check_ipv4_prefix, check_ipv6_prefix,\
    is_ipv4_prefix, is_ipv6_prefix, ValidationError
from noc.lib.ip import IP, IPv4


class Prefix(models.Model):
    """
    Allocated prefix
    """
    class Meta:
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
    asn = models.ForeignKey(
        AS, verbose_name=_("AS"),
        help_text=_("Autonomous system granted with prefix"),
        default=AS.default_as
    )
    project = models.ForeignKey(
        Project, verbose_name="Project",
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
    style = models.ForeignKey(Style, verbose_name=_("Style"), blank=True,
                              null=True)
    state = models.ForeignKey(
        ResourceState,
        verbose_name=_("State"),
        default=ResourceState.get_default)
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

    csv_ignored_fields = ["parent"]

    def __unicode__(self):
        return u"%s(%s): %s" % (self.vrf.name, self.afi, self.prefix)

    def get_absolute_url(self):
        return site.reverse("ip:ipam:vrf_index", self.vrf.id, self.afi,
                            self.prefix)

    @property
    def has_transition(self):
        """
        Check prefix has ipv4/ipv6 transition
        :return:
        """
        if self.afi == "4":
            return bool(self.ipv6_transition)
        else:
            try:
                self.ipv4_transition
                return True
            except Prefix.DoesNotExist:
                return False

    def clear_transition(self):
        if self.has_transition:
            if self.afi == "4":
                self.ipv6_transition = None
                self.save()
            else:
                self.ipv4_transition.ipv6_transition = None
                self.ipv4_transition.save()

    @classmethod
    def get_parent(cls, vrf, afi, prefix):
        """
        Get nearest closing prefix
        """
        r = list(Prefix.objects.raw("""
                SELECT id, prefix
                FROM ip_prefix
                WHERE
                        vrf_id=%s
                    AND afi=%s
                    AND prefix >> %s
                ORDER BY masklen(prefix) DESC
                LIMIT 1
                """,
            [vrf.id, str(afi), str(prefix)]))
        if not r:
            return None
        return r[0]

    @property
    def is_root(self):
        """
        Returns true if the prefix is a root of VRF
        """
        return (self.afi == "4" and self.prefix == "0.0.0.0/0") or (
        self.afi == "6" and self.prefix == "::/0")

    def clean(self):
        """
        Field validation
        """
        super(Prefix, self).clean()
        # Check prefix is of AFI type
        if self.afi == "4":
            check_ipv4_prefix(self.prefix)
        elif self.afi == "6":
            check_ipv6_prefix(self.prefix)
        # Check root prefix have no parent
        if self.is_root and self.parent:
            raise ValidationError("Root prefix cannot have parent")

    def save(self, **kwargs):
        """
        Save prefix
        """
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
        super(Prefix, self).save(**kwargs)
        # Rebuild tree if necessary
        # Reconnect children children prefixes
        c = connection.cursor()
        c.execute("""
            UPDATE %s
            SET    parent_id=%%s
            WHERE
                    vrf_id=%%s
                AND afi=%%s
                AND prefix << %%s
                AND parent_id=%%s
        """ % Prefix._meta.db_table,
            [self.id, self.vrf.id, self.afi, self.prefix,
             self.parent.id if self.parent else None]
        )
        # Reconnect children addresses
        c.execute("""
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
        if self.is_root:
            raise ValidationError("Cannot delete root prefix")
        # Reconnect children prefixes
        self.children_set.update(parent=self.parent)
        # Reconnect children addresses
        self.address_set.update(prefix=self.parent)
        # Unlink dual-stack allocations
        self.clear_transition()
        # Remove bookmarks
        self.prefixbookmark_set.all().delete()
        # Finally delete
        super(Prefix, self).delete(*args, **kwargs)

    def delete_recursive(self):
        """
        Delete prefix and all descendancies
        """
        # Unlink dual-stack allocations
        self.clear_transition()
        # Recursive delete
        c = connection.cursor()
        # Delete nested addresses
        c.execute("""
            DELETE FROM %s
            WHERE
                prefix_id IN
                    (
                    SELECT id
                    FROM %s
                    WHERE
                            vrf_id=%%s
                        AND afi=%%s
                        AND prefix <<= %%s
                    )""" % (Address._meta.db_table,
                            Prefix._meta.db_table),
            [self.vrf.id, self.afi, self.prefix]
        )
        # Delete nested prefixes
        c.execute("""
            DELETE FROM %s
            WHERE
                    vrf_id=%%s
                AND afi=%%s
                AND prefix <<= %%s
        """ % Prefix._meta.db_table, [self.vrf.id, self.afi, self.prefix])
        # Delete permissions
        c.execute("""
            DELETE FROM %s
            WHERE
                    vrf_id=%%s
                AND afi=%%s
                AND prefix=%%s
        """ % PrefixAccess._meta.db_table, [self.vrf.id, self.afi, self.prefix])

    @property
    def maintainers(self):
        """
        List of persons having write access
        @todo: PostgreSQL-independent implementation
        """
        return User.objects.raw("""
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
        try:
            PrefixBookmark.objects.get(user=user, prefix=self)
            return True
        except PrefixBookmark.DoesNotExist:
            return False

    ##
    ## Toggle user bookmark. Returns new bookmark state
    ##
    def toggle_bookmark(self, user):
        b, created = PrefixBookmark.objects.get_or_create(user=user,
                                                          prefix=self)
        if created:
            return True
        else:
            b.delete()
            return False

    ##
    ## Search engine plugin
    ##
    @classmethod
    def search(cls, user, query, limit):
        q = Q(description__icontains=query)
        if is_ipv4_prefix(query):
            q |= Q(afi="4", prefix=query)
        elif is_ipv6_prefix(query):
            q |= Q(afi="6", prefix=query)
        cq = CustomField.table_search_Q(cls._meta.db_table, query)
        if cq:
            q |= cq
        for o in cls.objects.filter(q):
            if query == o.prefix:
                relevancy = 1.0
            elif query in o.description:
                relevancy = float(len(query)) / float(len(o.description))
            else:
                relevancy = 0
            yield SearchResult(
                url=("ip:ipam:vrf_index", o.vrf.id, o.afi, o.prefix),
                title="VRF %s (IPv%s): %s (%s)" % (
                o.vrf.name, o.afi, o.prefix, o.description),
                text=unicode(o),
                relevancy=relevancy
            )

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

    def rebase(self, vrf, new_prefix):
        """
        Rebase prefix to a new location
        :param vrf:
        :param new_prefix:
        :return:
        """
        b = IP.prefix(self.prefix)
        nb = IP.prefix(new_prefix)
        # Rebase prefix and all nested prefixes
        # Parents are left untouched
        for p in Prefix.objects.filter(vrf=self.vrf, afi=self.afi).extra(
            where=["prefix <<= %s"], params=[self.prefix]):
            np = IP.prefix(p.prefix).rebase(b, nb).prefix
            # Prefix.objects.filter(pk=p.pk).update(prefix=np, vrf=vrf)
            p.prefix = np
            p.vrf = vrf
            p.save()  # Raise events
        # Rebase addresses
        # Parents are left untouched
        for a in Address.objects.filter(vrf=self.vrf, afi=self.afi).extra(
            where=["address <<= %s"], params=[self.prefix]):
            na = IP.prefix(a.address).rebase(b, nb).address
            # Address.objects.filter(pk=a.pk).update(address=na, vrf=vrf)
            a.address = na
            a.vrf = vrf
            a.save()  # Raise events
        # Rebase permissions
        # move all permissions to the nested blocks
        for pa in PrefixAccess.objects.filter(vrf=self.vrf).extra(
            where=["prefix <<= %s"], params=[self.prefix]):
            np = IP.prefix(pa.prefix).rebase(b, nb).prefix
            PrefixAccess.objects.filter(pk=pa.pk).update(
                prefix=np, vrf=vrf)
        # create permissions for covered blocks
        for pa in PrefixAccess.objects.filter(vrf=self.vrf).extra(
            where=["prefix >> %s"], params=[self.prefix]):
            PrefixAccess(user=pa.user, vrf=vrf, afi=pa.afi,
                prefix=new_prefix,  can_view=pa.can_view,
                can_change=pa.can_change).save()
        # @todo: Rebase bookmarks
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

# Avoid circular references
from address import Address
from prefixaccess import PrefixAccess
from prefixbookmark import PrefixBookmark
from addressrange import AddressRange
