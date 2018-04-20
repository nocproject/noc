# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# ManagedObjectSelector
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import operator
from threading import Lock
# Third-party modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
import cachetools
from psycopg2.extensions import adapt
# Third-party modules
import six
# NOC modules
from .administrativedomain import AdministrativeDomain
from .managedobjectprofile import ManagedObjectProfile
from .terminationgroup import TerminationGroup
from .profile import Profile
from noc.inv.models.vendor import Vendor
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
from noc.fm.models.ttsystem import TTSystem
from noc.main.models.pool import Pool
from noc.main.models.prefixtable import PrefixTable
from noc.core.model.fields import TagsField
from noc.lib.validators import check_re, is_int, is_ipv4, is_ipv6
from noc.lib.db import SQL, QTags
from noc.core.model.decorator import on_delete, on_save, on_delete_check
from noc.core.model.fields import DocumentReferenceField

id_lock = Lock()


@on_save
@on_delete
@on_delete_check(check=[
    # ("cm.SelectorItem", "selector"),
    ("fm.AlarmDiagnosticConfig", "selector"),
    # ("fm.EscalationItem", "selector"),
    ("fm.AlarmTrigger", "selector"),
    ("fm.EventTrigger", "selector"),
    ("inv.InterfaceClassificationRule", "selector"),
    ("inv.NetworkSegment", "selector"),
    ("sa.CommandSnippet", "selector"),
    ("sa.GroupAccess", "selector"),
    ("sa.ManagedObjectSelectorByAttribute", "selector"),
    ("sa.ObjectNotification", "selector"),
    ("sa.UserAccess", "selector"),
    ("vc.VCDomainProvisioningConfig", "selector"),
])
class ManagedObjectSelector(models.Model):
=======
##----------------------------------------------------------------------
## ManagedObjectSelector
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
## Third-party modules
import six
## NOC modules
from administrativedomain import AdministrativeDomain
from managedobject import ManagedObject, ManagedObjectAttribute
from managedobjectprofile import ManagedObjectProfile
from activator import Activator
from terminationgroup import TerminationGroup
from noc.main.models import Shard
from noc.main.models.prefixtable import PrefixTable
from noc.sa.profiles import profile_registry
from noc.lib.fields import TagsField
from noc.lib.validators import check_re, is_int, is_ipv4, is_ipv6
from noc.lib.db import SQL, QTags


class ManagedObjectSelector(models.Model):

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    class Meta:
        verbose_name = _("Managed Object Selector")
        verbose_name_plural = _("Managed Object Selectors")
        db_table = "sa_managedobjectselector"
        app_label = "sa"
        ordering = ["name"]

    name = models.CharField(_("Name"), max_length=64, unique=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    is_enabled = models.BooleanField(_("Is Enabled"), default=True)
    filter_id = models.IntegerField(_("Filter by ID"), null=True, blank=True)
    filter_name = models.CharField(_("Filter by Name (REGEXP)"),
<<<<<<< HEAD
                                   max_length=256, null=True, blank=True, validators=[check_re])
    filter_managed = models.NullBooleanField(
        _("Filter by Is Managed"),
        null=True, blank=True, default=True)
    filter_pool = DocumentReferenceField(Pool, null=True, blank=True)
    filter_profile = DocumentReferenceField(Profile, null=True, blank=True)
    filter_vendor = DocumentReferenceField(Vendor, null=True, blank=True)
    filter_platform = DocumentReferenceField(Platform, null=True, blank=True)
    filter_version = DocumentReferenceField(Firmware, null=True, blank=True)
    filter_object_profile = models.ForeignKey(ManagedObjectProfile,
                                              verbose_name=_("Filter by Object's Profile"), null=True, blank=True)
    filter_address = models.CharField(_("Filter by Address (REGEXP)"),
                                      max_length=256, null=True, blank=True, validators=[check_re])
    filter_prefix = models.ForeignKey(PrefixTable,
                                      verbose_name=_("Filter by Prefix Table"), null=True, blank=True)
    filter_administrative_domain = models.ForeignKey(AdministrativeDomain,
                                                     verbose_name=_("Filter by Administrative Domain"),
                                                     null=True, blank=True)
    filter_vrf = models.ForeignKey("ip.VRF",
                                   verbose_name=_("Filter by VRF"), null=True, blank=True)
    filter_vc_domain = models.ForeignKey("vc.VCDomain",
                                         verbose_name=_("Filter by VC Domain"), null=True, blank=True)
    filter_termination_group = models.ForeignKey(TerminationGroup,
                                                 verbose_name=_("Filter by termination group"), null=True, blank=True,
                                                 related_name="selector_termination_group_set"
                                                 )
    filter_service_terminator = models.ForeignKey(TerminationGroup,
                                                  verbose_name=_("Filter by service terminator"), null=True, blank=True,
                                                  related_name="selector_service_terminator_set"
                                                  )
    filter_tt_system = DocumentReferenceField(TTSystem, null=True, blank=True)
    filter_user = models.CharField(_("Filter by User (REGEXP)"),
                                   max_length=256, null=True, blank=True)
    filter_remote_path = models.CharField(_("Filter by Remote Path (REGEXP)"),
                                          max_length=256, null=True, blank=True, validators=[check_re])
    filter_description = models.CharField(_("Filter by Description (REGEXP)"),
                                          max_length=256, null=True, blank=True, validators=[check_re])
    filter_tags = TagsField(_("Filter By Tags"),
                            null=True, blank=True)
    source_combine_method = models.CharField(_("Source Combine Method"),
                                             max_length=1, default="O", choices=[("A", "AND"), ("O", "OR")])
    sources = models.ManyToManyField("self",
                                     verbose_name=_("Sources"), symmetrical=False,
                                     null=True, blank=True, related_name="sources_set")

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
=======
            max_length=256, null=True, blank=True, validators=[check_re])
    filter_managed = models.NullBooleanField(
        _("Filter by Is Managed"),
        null=True, blank=True, default=True)
    filter_profile = models.CharField(_("Filter by Profile"),
            max_length=64, null=True, blank=True,
            choices=profile_registry.choices)
    filter_object_profile = models.ForeignKey(ManagedObjectProfile,
            verbose_name=_("Filter by Object's Profile"), null=True, blank=True)
    filter_address = models.CharField(_("Filter by Address (REGEXP)"),
            max_length=256, null=True, blank=True, validators=[check_re])
    filter_prefix = models.ForeignKey(PrefixTable,
            verbose_name=_("Filter by Prefix Table"), null=True, blank=True)
    filter_shard = models.ForeignKey(Shard,
            verbose_name=_("Filter by Shard"), null=True, blank=True)
    filter_administrative_domain = models.ForeignKey(AdministrativeDomain,
            verbose_name=_("Filter by Administrative Domain"),
            null=True, blank=True)
    filter_activator = models.ForeignKey(Activator,
            verbose_name=_("Filter by Activator"), null=True, blank=True)
    filter_vrf = models.ForeignKey("ip.VRF",
            verbose_name=_("Filter by VRF"), null=True, blank=True)
    filter_vc_domain = models.ForeignKey("vc.VCDomain",
            verbose_name=_("Filter by VC Domain"), null=True, blank=True)
    filter_termination_group = models.ForeignKey(TerminationGroup,
            verbose_name=_("Filter by termination group"), null=True, blank=True,
            related_name="selector_termination_group_set"
            )
    filter_service_terminator = models.ForeignKey(TerminationGroup,
            verbose_name=_("Filter by service terminator"), null=True, blank=True,
            related_name="selector_service_terminator_set"
            )
    filter_user = models.CharField(_("Filter by User (REGEXP)"),
            max_length=256, null=True, blank=True)
    filter_remote_path = models.CharField(_("Filter by Remote Path (REGEXP)"),
            max_length=256, null=True, blank=True, validators=[check_re])
    filter_description = models.CharField(_("Filter by Description (REGEXP)"),
            max_length=256, null=True, blank=True, validators=[check_re])
    filter_tags = TagsField(_("Filter By Tags"),
            null=True, blank=True)
    source_combine_method = models.CharField(_("Source Combine Method"),
            max_length=1, default="O", choices=[("A", "AND"), ("O", "OR")])
    sources = models.ManyToManyField("self",
            verbose_name=_("Sources"), symmetrical=False,
            null=True, blank=True, related_name="sources_set")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def __unicode__(self):
        return self.name

<<<<<<< HEAD
    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        try:
            return ManagedObjectSelector.objects.get(id=id)
        except ManagedObjectSelector.DoesNotExist:
            return None

    def on_save(self):
        # Rebuild selector cache
        SelectorCache.refresh()

    def on_delete(self):
        # Rebuild selector cache
        SelectorCache.refresh()

=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @property
    def Q(self):
        """
        Returns Q object which can be applied to
        ManagedObject.objects.filter
        """
        # Exclude NOC internal objects
<<<<<<< HEAD
        q = ~Q(profile__in=list(Profile.objects.filter(name__startswith="NOC.")))
=======
        q = ~Q(profile_name__startswith="NOC.")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Exclude objects being wiped
        q &= ~Q(name__startswith="wiping-")
        # Filter by is_managed
        if self.filter_managed is not None:
            q &= Q(is_managed=self.filter_managed)
        # Filter by ID
        if self.filter_id:
            q &= Q(id=self.filter_id)
<<<<<<< HEAD
        # Filter by pool
        if self.filter_pool:
            q &= Q(pool=self.filter_pool)
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Filter by name (regex)
        if self.filter_name:
            q &= Q(name__regex=self.filter_name)
        # Filter by profile
        if self.filter_profile:
<<<<<<< HEAD
            q &= Q(profile=self.filter_profile)
        # Filter by vendor
        if self.filter_vendor:
            q &= Q(vendor=self.filter_vendor)
        # Filter by platform
        if self.filter_platform:
            q &= Q(platform=self.filter_platform)
        # Filter by version
        if self.filter_version:
            q &= Q(version=self.filter_version)
        # Filter by ttsystem
        if self.filter_tt_system:
            q &= Q(tt_system=self.filter_tt_system)
=======
            q &= Q(profile_name=self.filter_profile)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Filter by object's profile
        if self.filter_object_profile:
            q &= Q(object_profile=self.filter_object_profile)
        # Filter by address (regex)
        if self.filter_address:
            q &= Q(address__regex=self.filter_address)
        # Filter by prefix table
        if self.filter_prefix:
            q &= SQL("""
                EXISTS (
                    SELECT * FROM main_prefixtableprefix p
                    WHERE   table_id=%d
                        AND address::inet <<= p.prefix)""" % self.filter_prefix.id)
<<<<<<< HEAD
        # Filter by administrative domain
        if self.filter_administrative_domain:
            dl = AdministrativeDomain.get_nested_ids(
                self.filter_administrative_domain
            )
            q &= SQL("""
                "sa_managedobject"."administrative_domain_id" IN (%s)
            """ % ", ".join(str(x) for x in dl))
=======
        # Filter by shard
        if self.filter_shard:
            q &= Q(activator__shard=self.filter_shard)
        # Filter by administrative domain
        if self.filter_administrative_domain:
            q &= Q(administrative_domain=self.filter_administrative_domain)
        # Filter by activator
        if self.filter_activator:
            q &= Q(activator=self.filter_activator)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Filter by VRF
        if self.filter_vrf:
            q &= Q(vrf=self.filter_vrf)
        # Filter by VC domain
        if self.filter_vc_domain:
            q &= Q(vc_domain=self.filter_vc_domain)
        # Filter by termination group
        if self.filter_termination_group:
            q &= Q(termination_group=self.filter_termination_group)
        # Filter by termination group
        if self.filter_service_terminator:
            q &= Q(service_terminator=self.filter_service_terminator)
        # Filter by username
        if self.filter_user:
            q &= Q(user__regex=self.filter_user)
        # Filter by remote path
        if self.filter_remote_path:
            q &= Q(remote_path__regex=self.filter_remote_path)
        # Filter by description
        if self.filter_description:
            q &= Q(description__regex=self.filter_description)
        # Restrict to tags when necessary
        if self.filter_tags:
            q &= QTags(self.filter_tags)
        # Restrict to attributes when necessary
<<<<<<< HEAD
        for s in self.managedobjectselectorbyattribute_set.all():
            q &= SQL("""
                ("sa_managedobject"."id" IN (
                    SELECT managed_object_id
                    FROM sa_managedobjectattribute
                    WHERE
                        key ~ %s
                        AND value ~ %s
                ))
            """ % (
                adapt(s.key_re).getquoted(),
                adapt(s.value_re).getquoted()
            ))
=======
        # @todo: optimize with SQL
        m_ids = None
        for s in  self.managedobjectselectorbyattribute_set.all():
            ids = ManagedObjectAttribute.objects.filter(key__regex=s.key_re, value__regex=s.value_re).values_list("managed_object", flat=True)
            if m_ids is None:
                m_ids = set(ids)
            else:
                m_ids &= set(ids)
        if m_ids is not None:
            q &= Q(id__in=m_ids)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Restrict to sources
        if self.sources.count():
            if self.source_combine_method == "A":
                # AND
                for s in self.sources.all():
                    q &= s.Q
            else:
                # OR
                ql = list(self.sources.all())
                q = ql.pop(0).Q
                for qo in ql:
                    q |= qo.Q
        return q

    EXPR_MAP = [
        # Field, var, op
        ["filter_id", "id", "=="],
        ["filter_name", "name", "~"],
<<<<<<< HEAD
        ["filter_pool", "pool", "=="],
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        ["filter_profile", "profile", "=="],
        ["filter_object_profile", "object_profile", "=="],
        ["filter_address", "address", "~"],
        ["filter_prefix", "address", "IN"],
<<<<<<< HEAD
        ["filter_administrative_domain", "administrative_domain", "IN"],
=======
        ["filter_shard", "shard", "=="],
        ["filter_administrative_domain", "administrative_domain", "=="],
        ["filter_activator", "activator", "=="],
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        ["filter_vrf", "vrf", "=="],
        ["filter_vc_domain", "vc_domain", "=="],
        ["filter_termination_group", "termination_group", "=="],
        ["filter_service_terminator", "serivce_terminator", "=="],
        ["filter_user", "user", "=="],
        ["filter_remote_path", "remote_path", "~"],
        ["filter_description", "description", "~"],
        ["filter_tags", "tags", "CONTAINS"]
    ]

    @property
    def expr(self):
        """
        Return selector as text expression
        """
        def q(s):
            if isinstance(s, six.integer_types):
                return str(s)
            elif isinstance(s, (list, tuple)):
                s = [q(x) for x in s]
                return u"[%s]" % ", ".join(s)
            else:
                return u"\"%s\"" % unicode(s).replace("\\", "\\\\").replace("'", "\\'")

        expr = []
        # Filter by is_managed
        if self.filter_managed is not None:
            if self.filter_managed:
                expr += [u"IS MANAGED"]
            else:
                expr += [u"IS NOT MANAGED"]
        # Apply filters
        for f, n, op in self.EXPR_MAP:
            v = getattr(self, f)
            if v:
                expr += [u"%s %s %s" % (n, op, q(v))]
        # Apply attributes filters
        for s in self.managedobjectselectorbyattribute_set.all():
            expr += [u"attr(%s) ~ %s" % (q(s.key_re), q(s.value_re))]

        expr = [u" AND ".join(expr)]
        # Restrict to sources
        if self.sources.count():
            for s in self.sources.all():
                expr += [s.expr]
            op = u" AND " if self.source_combine_method == "A" else u" OR "
            expr = [op.join(u"(%s)" % x for x in expr)]
        return expr[0]

<<<<<<< HEAD
    @property
    def managed_objects(self):
        """
        Returns queryset containing managed objects
        :return:
        """
        from .managedobject import ManagedObject
        return ManagedObject.objects.filter(self.Q)

    def match(self, managed_object):
        """
        Check managed object matches selector
        :param managed_object:
        :return:
        """
=======
    ##
    ## Returns queryset containing managed objects
    ##
    @property
    def managed_objects(self):
        return ManagedObject.objects.filter(self.Q)

    ##
    ## Check Managed Object matches selector
    ##
    def match(self, managed_object):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return self.managed_objects.filter(id=managed_object.id).exists()

    def __contains__(self, managed_object):
        """
        "managed_object in selector"
        :param managed_object:
        :return:
        """
        return self.match(managed_object)

<<<<<<< HEAD
=======
    def scripts_profiles(self, scripts):
        """
        Returns a list of profile names supporting scripts
        :param scripts: List of script names
        :return: List of profile names
        """
        sp = set()
        for p in profile_registry.classes:
            skip = False
            for s in scripts:
                if s not in profile_registry[p].scripts:
                    skip = True
                    continue
            if not skip:
                sp.add(p)
        return list(sp)

    ##
    ## Returns queryset containing managed objects supporting scripts
    ##
    def objects_with_scripts(self, scripts):
        return self.managed_objects.filter(
            profile_name__in=self.scripts_profiles(scripts))

    def objects_for_user(self, user, scripts=None):
        """
        Returns queryset containing selector objects accessible to user,
        optionally restricted to ones having scripts
        :param user: User
        :param scripts: optional list of scripts
        :return:
        """
        q = UserAccess.Q(user)
        if scripts:
            q &= Q(profile_name__in=self.scripts_profiles(scripts))
        return self.managed_objects.filter(q)

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    @classmethod
    def resolve_expression(cls, s):
        """
        Resolve expression to a list of object.

        Expression must be string or list.
        Elements must be one of:
        * string starting with @ - treated as selector name
        * string containing numbers - treated as object's id
        * string - managed object name.
        * string - IPv4 or IPv6 address - management address

        Raises ManagedObject.DoesNotExists if object is not found.
        Raises ManagedObjectSelector.DoesNotExists if selector is not found
        :param cls:
        :param s:
        :return:
        """
<<<<<<< HEAD
        from .managedobject import ManagedObject

=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        if type(s) in (int, long, str, unicode):
            s = [s]
        if type(s) != list:
            raise ValueError("list required")
        objects = set()
        for so in s:
<<<<<<< HEAD
            if not isinstance(so, six.string_types):
=======
            if not isinstance(so, basestring):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                so = str(so)
            if so.startswith("@"):
                # Selector expression: @<selector name>
                o = ManagedObjectSelector.objects.get(name=so[1:])
                objects |= set(o.managed_objects)
            else:
                # Search by name
                q = Q(name=so)
                if is_int(so):
                    # Search by id
                    q |= Q(id=int(so))
                if is_ipv4(so) or is_ipv6(so):
                    q |= Q(address=so)
                o = ManagedObject.objects.get(q)
                objects.add(o)
        return list(objects)


class ManagedObjectSelectorByAttribute(models.Model):
    class Meta:
        verbose_name = _("Managed Object Selector by Attribute")
<<<<<<< HEAD
=======
        verbose_name = _("Managed Object Selectors by Attribute")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        db_table = "sa_managedobjectselectorbyattribute"
        app_label = "sa"

    selector = models.ForeignKey(ManagedObjectSelector,
<<<<<<< HEAD
                                 verbose_name=_("Object Selector"))
    key_re = models.CharField(_("Filter by key (REGEXP)"),
                              max_length=256, validators=[check_re])
    value_re = models.CharField(_("Filter by value (REGEXP)"),
                                max_length=256, validators=[check_re])
=======
            verbose_name=_("Object Selector"))
    key_re = models.CharField(_("Filter by key (REGEXP)"),
            max_length=256, validators=[check_re])
    value_re = models.CharField(_("Filter by value (REGEXP)"),
            max_length=256, validators=[check_re])
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def __unicode__(self):
        return u"%s: %s = %s" % (
            self.selector.name, self.key_re, self.value_re)

<<<<<<< HEAD

# Avoid circular references
from .selectorcache import SelectorCache
=======
# Avoid circular references
from useraccess import UserAccess
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
