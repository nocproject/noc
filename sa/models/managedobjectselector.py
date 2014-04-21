# -*- coding: utf-8 -*-
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
            max_length=256, null=True, blank=True, validators=[check_re])
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
    filter_repo_path = models.CharField(_("Filter by Repo Path (REGEXP)"),
            max_length=256, null=True, blank=True, validators=[check_re])
    filter_tags = TagsField(_("Filter By Tags"),
            null=True, blank=True)
    source_combine_method = models.CharField(_("Source Combine Method"),
            max_length=1, default="O", choices=[("A", "AND"), ("O", "OR")])
    sources = models.ManyToManyField("self",
            verbose_name=_("Sources"), symmetrical=False,
            null=True, blank=True, related_name="sources_set")

    def __unicode__(self):
        return self.name

    ##
    ## Returns a Q object
    ##
    @property
    def Q(self):
        # Apply restrictions
        q = Q(is_managed=True) & ~Q(profile_name__startswith="NOC.")
        # Filter by ID
        if self.filter_id:
            q &= Q(id=self.filter_id)
        # Filter by name (regex)
        if self.filter_name:
            q &= Q(name__regex=self.filter_name)
        # Filter by profile
        if self.filter_profile:
            q &= Q(profile_name=self.filter_profile)
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
        # Filter by shard
        if self.filter_shard:
            q &= Q(activator__shard=self.filter_shard)
        # Filter by administrative domain
        if self.filter_administrative_domain:
            q &= Q(administrative_domain=self.filter_administrative_domain)
        # Filter by activator
        if self.filter_activator:
            q &= Q(activator=self.filter_activator)
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
        # Filter by repo path
        if self.filter_repo_path:
            q &= Q(repo_path__regex=self.filter_repo_path)
        # Restrict to tags when necessary
        if self.filter_tags:
            q &= QTags(self.filter_tags)
        # Restrict to attributes when necessary
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
        return self.managed_objects.filter(id=managed_object.id).exists()

    def __contains__(self, managed_object):
        """
        "managed_object in selector"
        :param managed_object:
        :return:
        """
        return self.match(managed_object)

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
        if type(s) in (int, long, str, unicode):
            s = [s]
        if type(s) != list:
            raise ValueError("list required")
        objects = set()
        for so in s:
            if not isinstance(so, basestring):
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
        verbose_name = _("Managed Object Selectors by Attribute")
        db_table = "sa_managedobjectselectorbyattribute"
        app_label = "sa"

    selector = models.ForeignKey(ManagedObjectSelector,
            verbose_name=_("Object Selector"))
    key_re = models.CharField(_("Filter by key (REGEXP)"),
            max_length=256, validators=[check_re])
    value_re = models.CharField(_("Filter by value (REGEXP)"),
            max_length=256, validators=[check_re])

    def __unicode__(self):
        return u"%s: %s = %s" % (
            self.selector.name, self.key_re, self.value_re)

# Avoid circular references
from useraccess import UserAccess
