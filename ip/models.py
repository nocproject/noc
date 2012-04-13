# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
from operator import attrgetter
# Django Modules
from django.utils.translation import ugettext_lazy as _
from django.db import connection, models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.template import Template, Context
# NOC Modules
from noc.main.models import Style, ResourceState
from noc.peer.models import AS
from noc.vc.models import VC
from noc.sa.models import ManagedObject
from noc.lib.app import site
from noc.lib.fields import CIDRField, MACField, INETField, AutoCompleteTagsField
from noc.lib.validators import *
from noc.lib.ip import *
from noc.lib.search import SearchResult

##
## Address Family choices
##
AFI_CHOICES = [
    ("4", _("IPv4")),
    ("6", _("IPv6"))
]


class VRFGroup(models.Model):
    """
    Group of VRFs with common properties
    """
    class Meta:
        verbose_name = _("VRF Group")
        verbose_name_plural = _("VRF Groups")
        ordering = ["name"]

    name = models.CharField(_("VRF Group"), unique=True, max_length=64,
                            help_text=_("Unique VRF Group name"))
    address_constraint = models.CharField(_("Address Constraint"), max_length=1,
                                          choices=[("V", _(
                                              "Addresses are unique per VRF")),
                                              ("G", _("Addresses are unique per VRF Group"))],
                                          default="V")
    description = models.TextField(_("Description"), blank=True, null=True)
    tags = AutoCompleteTagsField(_("Tags"), null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

    def get_absolute_url(self):
        return site.reverse("ip:vrfgroup:change", self.id)


class VRF(models.Model):
    """
    VRF
    """
    class Meta:
        verbose_name = _("VRF")
        verbose_name_plural = _("VRFs")
        ordering = ["name"]

    name = models.CharField(_("VRF"), unique=True, max_length=64,
                            help_text=_("Unique VRF Name"))
    vrf_group = models.ForeignKey(VRFGroup, verbose_name=_("VRF Group"))
    rd = models.CharField(_("RD"), unique=True, max_length=21,
                          validators=[check_rd],
                          help_text=_(
                              "Route Distinguisher in form of ASN:N or IP:N"))
    afi_ipv4 = models.BooleanField(_("IPv4"), default=True,
                                   help_text=_("Enable IPv4 Address Family"))
    afi_ipv6 = models.BooleanField(_("IPv6"), default=False,
                                   help_text=_("Enable IPv6 Address Family"))
    description = models.TextField(_("Description"), blank=True, null=True)
    tt = models.IntegerField(_("TT"), blank=True, null=True,
                             help_text=_("Ticket #"))
    tags = AutoCompleteTagsField(_("Tags"), null=True, blank=True)
    style = models.ForeignKey(Style, verbose_name=_("Style"), blank=True,
                              null=True)
    state = models.ForeignKey(ResourceState, verbose_name=_("State"),
                              default=ResourceState.get_default)
    allocated_till = models.DateField(_("Allocated till"), null=True,
                                      blank=True,
                                      help_text=_("VRF temporary allocated till the date"))

    def __unicode__(self):
        if self.rd == "0:0":
            return u"global"
        else:
            return self.name

    def get_absolute_url(self):
        return site.reverse("ip:vrf:change", self.id)

    @classmethod
    def get_global(self):
        """
        Returns VRF 0:0
        """
        return VRF.objects.get(rd="0:0")

    def save(self, **kwargs):
        """
        Create root entries for all enabled AFIs
        """
        super(VRF, self).save(**kwargs)
        if self.afi_ipv4:
            # Create IPv4 root, if not exists
            Prefix.objects.get_or_create(vrf=self, afi="4", prefix="0.0.0.0/0",
                                         defaults={"asn": AS.default_as(),
                                                   "description": "IPv4 Root"})
        if self.afi_ipv6:
            # Create IPv6 root, if not exists
            Prefix.objects.get_or_create(vrf=self, afi="6", prefix="::/0",
                                         defaults={"asn": AS.default_as(),
                                                   "description": "IPv6 Root"})

    @classmethod
    def search(cls, user, query, limit):
        """
        Search engine plugin
        """
        q = Q(name__icontains=query)
        if is_rd(query):
            q |= Q(rd=query)
        for o in cls.objects.filter(q):
            relevancy = 1.0
            yield SearchResult(
                url=("ip:vrf:change", o.id),
                title="VRF: " + unicode(o),
                text=unicode(o),
                relevancy=relevancy
            )


class Prefix(models.Model):
    """
    Allocated prefix
    """
    class Meta:
        verbose_name = _("Prefix")
        verbose_name_plural = _("Prefixes")
        unique_together = [("vrf", "afi", "prefix")]

    parent = models.ForeignKey("self", related_name="children_set",
                               verbose_name=_("Parent"), null=True, blank=True)
    vrf = models.ForeignKey(VRF, verbose_name=_("VRF"))
    afi = models.CharField(_("Address Family"), max_length=1,
                           choices=AFI_CHOICES)
    prefix = CIDRField(_("Prefix"))
    asn = models.ForeignKey(AS, verbose_name=_("AS"),
                            help_text=_(
                                "Authonomous system granted with prefix"))
    vc = models.ForeignKey(VC, verbose_name=_("VC"), null=True, blank=True,
                           on_delete=models.SET_NULL,
                           help_text=_("VC bound to prefix"))
    description = models.TextField(_("Description"), blank=True, null=True)
    tags = AutoCompleteTagsField("Tags", null=True, blank=True)
    tt = models.IntegerField("TT", blank=True, null=True,
                             help_text=_("Ticket #"))
    style = models.ForeignKey(Style, verbose_name=_("Style"), blank=True,
                              null=True)
    state = models.ForeignKey(ResourceState, verbose_name=_("State"),
                              default=ResourceState.get_default)
    allocated_till = models.DateField(_("Allocated till"), null=True,
                                      blank=True,
                                      help_text=_("VRF temporary allocated till the date"))

    def __unicode__(self):
        return u"%s(%s): %s" % (self.vrf.name, self.afi, self.prefix)

    def get_absolute_url(self):
        return site.reverse("ip:ipam:vrf_index", self.vrf.id, self.afi,
                            self.prefix)

    @classmethod
    def get_parent(cls, vrf, afi, prefix):
        """
        Get nearest closing prefix
        """
        r = list(Prefix.objects.raw("""
                SELECT id,prefix
                FROM  %s
                WHERE
                        vrf_id=%%s
                    AND afi=%%s
                    AND prefix >> %%s
                ORDER BY masklen(prefix) DESC
                LIMIT 1
                """ % cls._meta.db_table, [vrf.id, afi, str(prefix)]))
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
        if not self.is_root:
            # Set proper parent
            self.parent = Prefix.get_parent(self.vrf, self.afi, self.prefix)
        self.afi = "6" if ":" in self.prefix else "4"
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
             self.parent.id if self.parent else None])
        # Reconnect children addresses
        c.execute("""
            UPDATE %s
            SET prefix_id=%%s
            WHERE
                    prefix_id=%%s
                AND address << %%s
                """ % Address._meta.db_table,
            [self.id, self.parent.id if self.parent else None, self.prefix])

    def delete(self, *args, **kwargs):
        """
        Delete prefix
        """
        if self.is_root:
            raise ValidationError("Cannot delete root prefix")
        parent = self.parent
        # Reconnect children prefixes
        self.children_set.update(parent=self.parent)
        # Reconnect children addresses
        self.address_set.update(prefix=self.parent)
        # Finally delete
        super(Prefix, self).delete(*args, **kwargs)

    def delete_recursive(self):
        """
        Delete prefix and all descendancies
        """
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
                    )""" % (Address._meta.db_table, Prefix._meta.db_table),
            [self.vrf.id, self.afi, self.prefix])
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
        return PrefixAccess.user_can_view(user, self.vrf, self.afi, self.prefix)

    ##
    ## Return True if user has change access
    ##
    def can_change(self, user):
        return PrefixAccess.user_can_change(user, self.vrf, self.afi,
                                            self.prefix)

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

    ##
    ## Rebase prefix to a new location
    ##
    def rebase(self, vrf, new_prefix):
        c = connection.cursor()
        b = IP.prefix(self.prefix)
        nb = IP.prefix(new_prefix)
        # Rebase nested prefixes
        r = []  # (prefix, new_prefix)
        for p in Prefix.objects.raw("""
            SELECT *
            FROM   ip_prefix
            WHERE
                    vrf_id=%s
                AND prefix<<=%s
        """, [self.vrf.id, self.prefix]):
            pp = IP.prefix(p.prefix)
            r += [(p.prefix, pp.rebase(b, nb).prefix)]
        for op, np in r:
            c.execute(
                "UPDATE ip_prefix SET prefix=%s, vrf_id=%s WHERE prefix=%s AND vrf_id=%s",
                [np, vrf.id, op, self.vrf.id])
            # Rebase addresses
        r = []
        for a in Address.objects.raw("""
            SELECT  *
            FROM    ip_address
            WHERE
                    vrf_id=%s
                AND address<<=%s
        """, [self.vrf.id, self.prefix]):
            r += [(a.address, IP.prefix(a.address).rebase(b, nb).address)]
        for oa, na in r:
            c.execute(
                "UPDATE ip_address SET address=%s, vrf_id=%s WHERE address=%s AND vrf_id=%s",
                [na, vrf.id, oa, self.vrf.id])
        # Rebase permissions
        # move all permissions to the nested blocks
        r = set([a.prefix for a in PrefixAccess.objects.raw("""
            SELECT  *
            FROM    ip_prefixaccess
            WHERE
                    vrf_id=%s
                AND prefix<<=%s
            """, [self.vrf.id, self.prefix])])
        for p in r:
            np = IP.prefix(p).rebase(b, nb).prefix
            c.execute(
                "UPDATE ip_prefixaccess SET prefix=%s, vrf_id=%s WHERE prefix=%s AND vrf_id=%s",
                [np, vrf.id, p, self.vrf.id])
            # create permissions for covered blocks
        for a in PrefixAccess.objects.raw("""
            SELECT  *
            FROM    ip_prefixaccess
            WHERE
                    vrf_id=%s
                AND prefix >> %s
            """, [self.vrf.id, self.prefix]):
            PrefixAccess(user=a.user, vrf=vrf, afi=a.afi, prefix=new_prefix,
                         can_view=a.can_view, can_change=a.can_change).save()
            # Return rebased prefix
        return Prefix.objects.get(vrf=vrf, prefix=new_prefix)

    @property
    def nested_address_set(self):
        """
        Queryset returning all nested addresses inside the prefix
        """
        return Address.objects.filter(vrf=self.vrf, afi=self.afi).extra(
            where=["address <<= %s"], params=[self.prefix])


##
## Allocate address
##
class Address(models.Model):
    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        unique_together = [("prefix", "vrf", "afi", "address")]

    prefix = models.ForeignKey(Prefix, verbose_name=_("Prefix"))
    vrf = models.ForeignKey(VRF, verbose_name=_("VRF"))
    afi = models.CharField(_("Address Family"), max_length=1,
                           choices=AFI_CHOICES)
    address = INETField(_("Address"))
    fqdn = models.CharField(_("FQDN"), max_length=255,
                            help_text=_("Full-qualified Domain Name"),
                            validators=[check_fqdn])
    mac = MACField("MAC", null=True, blank=True, help_text=_("MAC Address"))
    auto_update_mac = models.BooleanField("Auto Update MAC", default=False,
                                          help_text=_(
                                              "Set to auto-update MAC field"))
    managed_object = models.ForeignKey(ManagedObject,
                                       verbose_name=_("Managed Object"),
                                       null=True, blank=True,
                                       related_name="address_set",
                                       on_delete=models.SET_NULL,
                                       help_text=_(
                                           "Set if address belongs to the Managed Object's interface"))
    description = models.TextField(_("Description"), blank=True, null=True)
    tags = AutoCompleteTagsField(_("Tags"), null=True, blank=True)
    tt = models.IntegerField(_("TT"), blank=True, null=True,
                             help_text=_("Ticket #"))
    style = models.ForeignKey(Style, verbose_name=_("Style"), blank=True,
                              null=True)
    state = models.ForeignKey(ResourceState, verbose_name=_("State"),
                              default=ResourceState.get_default)
    allocated_till = models.DateField(_("Allocated till"), null=True, blank=True,
                                      help_text=_("VRF temporary allocated till the date"))

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

    ##
    ## Save address
    ##
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
        super(Address, self).save(**kwargs)

    ##
    ## Field validation
    ##
    def clean(self):
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

    ##
    ## Search engine plugin
    ##
    @classmethod
    def search(cls, user, query, limit):
        q = Q(description__icontains=query) | Q(fqdn__icontains=query)
        if is_ipv4(query):
            q |= Q(afi="4", address=query)
        elif is_ipv6(query):
            q |= Q(afi="6", address=query)
        for o in cls.objects.filter(q):
            if query == o.address:
                relevancy = 1.0
            elif query in o.fqdn:
                relevancy = float(len(query)) / float(len(o.fqdn))
            elif o.description and query in o.description:
                relevancy = float(len(query)) / float(len(o.description))
            else:
                relevancy = 0
            yield SearchResult(
                url=("ip:ipam:vrf_index", o.vrf.id, o.afi, o.prefix.prefix),
                title="VRF %s (IPv%s): %s (%s)" % (
                o.vrf.name, o.afi, o.address, o.description),
                text=unicode(o),
                relevancy=relevancy
            )


##
## Prefix Access
##
class PrefixAccess(models.Model):
    class Meta:
        verbose_name = _("Prefix Access")
        verbose_name_plural = _("Prefix Access")
        unique_together = [("user", "vrf", "afi", "prefix")]
        ordering = ["user", "vrf", "afi", "prefix"]

    user = models.ForeignKey(User, verbose_name=_("User"))
    vrf = models.ForeignKey(VRF, verbose_name=_("VRF"))
    afi = models.CharField(_("Address Family"), max_length=1,
                           choices=AFI_CHOICES)
    prefix = CIDRField(_("Prefix"))
    can_view = models.BooleanField(_("Can View"), default=False)
    can_change = models.BooleanField(_("Can Change"), default=False)

    def __unicode__(self):
        perms = []
        if self.can_view:
            perms += ["View"]
        if self.can_change:
            perms += ["Change"]
        return u"%s: %s(%s): %s: %s" % (
        self.user.username, self.vrf.name, self.afi, self.prefix,
        ", ".join(perms))

    ##
    ## Field validation
    ##
    def clean(self):
        super(PrefixAccess, self).clean()
        # Check prefix is of AFI type
        if self.afi == "4":
            check_ipv4_prefix(self.prefix)
        elif self.afi == "6":
            check_ipv6_prefix(self.prefix)

    ##
    ## Check user has read access to prefix
    ##
    @classmethod
    def user_can_view(self, user, vrf, afi, prefix):
        if user.is_superuser:
            return True
        if isinstance(prefix, Prefix):
            prefix = prefix.prefix
        else:
            prefix = str(prefix)
            # @todo: PostgreSQL-independed implementation
        c = connection.cursor()
        c.execute("""SELECT COUNT(*)
                     FROM %s
                     WHERE prefix >>= %%s
                        AND vrf_id=%%s
                        AND afi=%%s
                        AND user_id=%%s
                        AND can_view=TRUE
                 """ % PrefixAccess._meta.db_table,
            [str(prefix), vrf.id, afi, user.id])
        return c.fetchall()[0][0] > 0

    ##
    ## Check user has write access to prefix
    ##
    @classmethod
    def user_can_change(self, user, vrf, afi, prefix):
        if user.is_superuser:
            return True
            # @todo: PostgreSQL-independed implementation
        c = connection.cursor()
        c.execute("""SELECT COUNT(*)
                     FROM %s
                     WHERE prefix >>= %%s
                        AND vrf_id=%%s
                        AND afi=%%s
                        AND user_id=%%s
                        AND can_change=TRUE
                 """ % PrefixAccess._meta.db_table,
            [str(prefix), vrf.id, afi, user.id])
        return c.fetchall()[0][0] > 0


##
## Address Ranges
##
class AddressRange(models.Model):
    class Meta:
        verbose_name = _("Address Range")
        verbose_name = _("Address Ranges")
        unique_together = [("vrf", "afi", "from_address", "to_address")]

    name = models.CharField(_("Name"), max_length=64, unique=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    vrf = models.ForeignKey(VRF, verbose_name=_("VRF"))
    afi = models.CharField(_("Address Family"), max_length=1,
                           choices=AFI_CHOICES)
    from_address = CIDRField(_("From Address"))
    to_address = CIDRField(_("To address"))
    description = models.TextField(_("Description"), blank=True, null=True)
    is_locked = models.BooleanField(_("Is Locked"), default=False,
                                    help_text=_(
                                        "Check to deny address creation or editing within the range"))
    action = models.CharField(_("Action"), max_length=1,
                              choices=[("N", _("Do nothing")),
                                  ("G", _("Generate FQDNs")),
                                  ("D", _("Partial reverse zone delegation"))],
                              default="N")
    fqdn_template = models.CharField(_("FQDN Template"), max_length=255,
                                     null=True, blank=True,
                                     help_text=_(
                                         "Template to generate FQDNs when 'Action' set to 'Generate FQDNs'"))
    reverse_nses = models.CharField(_("Reverse NSes"), max_length=255,
                                    null=True, blank=True,
                                    help_text=_(
                                        "Comma-separated list of NSes to partial reverse zone delegation when 'Action' set to 'Partial reverse zone delegation"))
    tags = AutoCompleteTagsField(_("Tags"), null=True, blank=True)
    tt = models.IntegerField("TT", blank=True, null=True,
                             help_text=_("Ticket #"))
    allocated_till = models.DateField(_("Allocated till"), null=True, blank=True,
                                      help_text=_("VRF temporary allocated till the date"))

    def __unicode__(self):
        return u"%s (IPv%s): %s -- %s" % (
        self.vrf.name, self.afi, self.from_address, self.to_address)

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

    ##
    ##
    ##
    def get_absolute_url(self):
        return site.reverse("ip:addressrange:change", self.id)

    ##
    ## Save instance
    ##
    def save(self, **kwargs):
        def generate_fqdns():
            # Prepare FQDN template
            t = Template(self.fqdn_template)
            # Sync FQDNs
            sn = 0
            for ip in self.addresses:
                # Generage FQDN
                vars = {"afi": self.afi, "vrf": self.vrf, "range": self,
                        "n": sn}
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
                description = "Generated by address range '%s'" % (self.name)
                # Create or update address record when necessary
                a, created = Address.objects.get_or_create(vrf=self.vrf,
                                                           afi=self.afi,
                                                           address=ip.address)
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
                    Address.objects.filter(vrf=self.vrf, afi=self.afi,
                                           address__gte=old.from_address,
                                           address__lt=self.to_address).delete()
                if IP.prefix(old.to_address) > IP.prefix(self.to_address):
                    # Upper boundary is lowered. Clean up addressess falled out of range
                    Address.objects.filter(vrf=self.vrf, afi=self.afi,
                                           address__gt=self.to_address,
                                           address__lte=old.to_address).delete()
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

    ##
    ## Returns a list of overlapping ranges
    ##
    @classmethod
    def get_overlapping_ranges(cls, vrf, afi, from_address, to_address):
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
        """, {"vrf": vrf.id, "afi": afi, "from_address": from_address,
              "to_address": to_address})

    ##
    ## Returns a queryset with overlapped ranges
    ##
    @property
    def overlapping_ranges(self):
        return self.get_overlapping_ranges(self.vrf, self.afi,
                                           self.from_address, self.to_address)

    @classmethod
    def address_is_locked(cls, vrf, afi, address):
        """
        Check wrether address is locked by any range
        """
        return AddressRange.objects.filter(vrf=vrf, afi=afi, is_locked=True,
                                           is_active=True,
                                           from_address__lte=address,
                                           to_address__gte=address).exists()


class PrefixBookmark(models.Model):
    """
    User Bookmarks
    """
    class Meta:
        verbose_name = _("Prefix Bookmark")
        verbose_name_plural = _("Prefix Bookmarks")
        unique_together = [("user", "prefix")]

    user = models.ForeignKey(User, verbose_name="User")
    prefix = models.ForeignKey(Prefix, verbose_name="Prefix")

    def __unicode__(self):
        return u"Bookmark at %s for %s" % (self.prefix, self.user.username)

    ##
    ## Returns a prefixes bookmarked by user
    ##
    @classmethod
    def user_bookmarks(cls, user, vrf=None, afi=None):
        q = Q(user=user)
        if vrf:
            if afi:
                q &= Q(prefix__vrf=vrf, prefix__afi=afi)
            else:
                q &= Q(prefix__vrf=vrf)
        return sorted([b.prefix for b in cls.objects.filter(q)], key=attrgetter(
            "prefix"))
