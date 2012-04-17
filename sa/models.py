# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Models for "sa" module
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import marshal
import base64
import datetime
import random
import cPickle
import time
import types
import re
from collections import defaultdict
## Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
from django.db import IntegrityError
from django.contrib.auth.models import User, Group
## Third-party modules
from tagging.models import TaggedItem
## NOC modules
from noc.main.models import PyRule, Shard, PrefixTable, Permission
from noc.sa.profiles import profile_registry
from noc.sa.script import script_registry
from noc.sa.protocols.sae_pb2 import *
from noc.lib.search import SearchResult
from noc.lib.fields import PickledField, INETField, AutoCompleteTagsField
from noc.lib.app.site import site
from noc.lib.validators import check_re
from noc.lib.db import SQL
from noc.lib import nosql
##
## Register objects
##
profile_registry.register_all()
script_registry.register_all()
scheme_choices = [(TELNET, "telnet"), (SSH, "ssh"), (HTTP, "http")]


class AdministrativeDomain(models.Model):
    """
    Administrative Domain
    """
    
    class Meta:
        verbose_name = _("Administrative Domain")
        verbose_name_plural = _("Administrative Domains")
        ordering = ["name"]
    
    name = models.CharField(_("Name"), max_length=32, unique=True)
    description = models.TextField(_("Description"), null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    

class Activator(models.Model):
    """
    Activator
    """
    
    class Meta:
        verbose_name = _("Activator")
        verbose_name_plural = _("Activators")
        ordering = ["name"]
    
    name = models.CharField(_("Name"), max_length=32, unique=True)
    shard = models.ForeignKey(Shard, verbose_name=_("Shard"))
    ip = models.IPAddressField(_("From IP"))
    to_ip = models.IPAddressField(_("To IP"))
    auth = models.CharField(_("Auth String"), max_length=64)
    is_active = models.BooleanField(_("Is Active"), default=True)
    tags = AutoCompleteTagsField(_("Tags"), null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return site.reverse("sa:activator:change", self.id)
    
    @classmethod
    def check_ip_access(self, ip):
        """
        Check IP belongs to any activator
        
        :param ip: IP address
        :type ip: String
        :rtype: Bool
        """
        return Activator.objects.filter(ip__gte=ip, to_ip__lte=ip).exists()

    @property
    def capabilities(self):
        """
        Get current activator pool capabilities in form of dict or None
        """
        c = ActivatorCapabilitiesCache.objects.filter(activator_id=self.id).first()
        if c is None:
            return {
                "members": 0,
                "max_scripts": 0
            }
        else:
            return {
                "members": c.members,
                "max_scripts": c.max_scripts
            }

    def update_capabilities(self, members, max_scripts):
        """
        Update activator pool capabilities

        :param members: Active members in pool. Pool considered inactive when
                        members == 0
        :param max_scripts: Maximum amount of concurrent scripts in pool
        """
        c = ActivatorCapabilitiesCache.objects.filter(activator_id=self.id).first()
        if c:
            c.members = members
            c.max_scripts = max_scripts
            c.save()
        else:
            ActivatorCapabilitiesCache(activator_id=self.id, members=members,
                                       max_scripts=max_scripts).save()


class ManagedObject(models.Model):
    """
    Managed Object
    """
    
    class Meta:
        verbose_name = _("Managed Object")
        verbose_name_plural = _("Managed Objects")
        ordering = ["name"]
    
    name = models.CharField(_("Name"), max_length=64, unique=True)
    is_managed = models.BooleanField(_("Is Managed?"), default=True)
    administrative_domain = models.ForeignKey(AdministrativeDomain,
            verbose_name=_("Administrative Domain"))
    activator = models.ForeignKey(Activator,
            verbose_name=_("Activator"),
            limit_choices_to={"is_active": True})
    profile_name = models.CharField(_("Profile"),
            max_length=128, choices=profile_registry.choices)
    description = models.CharField(_("Description"),
            max_length=256, null=True, blank=True)
    # Access
    scheme = models.IntegerField(_("Scheme"), choices=scheme_choices)
    address = models.CharField(_("Address"), max_length=64)
    port = models.PositiveIntegerField(_("Port"), blank=True, null=True)
    user = models.CharField(_("User"), max_length=32, blank=True, null=True)
    password = models.CharField(_("Password"),
            max_length=32, blank=True, null=True)
    super_password = models.CharField(_("Super Password"),
            max_length=32, blank=True, null=True)
    remote_path = models.CharField(_("Path"),
            max_length=256, blank=True, null=True)
    trap_source_ip = INETField(_("Trap Source IP"), null=True,
            blank=True, default=None)
    trap_community = models.CharField(_("Trap Community"),
            blank=True, null=True, max_length=64)
    snmp_ro = models.CharField(_("RO Community"),
            blank=True, null=True, max_length=64)
    snmp_rw = models.CharField(_("RW Community"),
            blank=True, null=True, max_length=64)
    # CM
    is_configuration_managed = models.BooleanField(_("Is Configuration Managed?"),
            default=True)
    repo_path = models.CharField(_("Repo Path"),
            max_length=128, blank=True, null=True)
    # Default VRF
    vrf = models.ForeignKey("ip.VRF", verbose_name=_("VRF"),
                            blank=True, null=True)
    # pyRules
    config_filter_rule = models.ForeignKey(PyRule,
            verbose_name="Config Filter pyRule", 
            limit_choices_to={"interface": "IConfigFilter"},
            null=True, blank=True,
            related_name="managed_object_config_filter_rule_set")
    config_diff_filter_rule = models.ForeignKey(PyRule,
            verbose_name=_("Config Diff Filter Rule"),
            limit_choices_to={"interface": "IConfigDiffFilter"},
            null=True, blank=True,
            related_name="managed_object_config_diff_rule_set")
    config_validation_rule = models.ForeignKey(PyRule,
            verbose_name="Config Validation pyRule",
            limit_choices_to={"interface": "IConfigValidator"},
            null=True, blank=True,
            related_name="managed_object_config_validation_rule_set")
    max_scripts = models.IntegerField(_("Max. Scripts"),
            null=True, blank=True,
            help_text=_("Concurrent script session limits"))
    #
    tags = AutoCompleteTagsField(_("Tags"), null=True, blank=True)
    
    # Use special filter for profile
    profile_name.existing_choices_filter = True  
    
    ## object.scripts. ...
    class ScriptsProxy(object):
        class CallWrapper(object):
            def __init__(self, obj, name):
                self.name = name
                self.object = obj
            
            def __call__(self, **kwargs):
                task = ReduceTask.create_task([self.object],
                    reduce_object_script, {},
                    self.name, kwargs, None)
                return task.get_result(block=True)
        
        def __init__(self, obj):
            self._object = obj
            self._cache = {}
        
        def __getattr__(self, name):
            if name in self._cache:
                return self._cache[name]
            if name not in self._object.profile.scripts:
                raise AttributeError(name)
            cw = ManagedObject.ScriptsProxy.CallWrapper(self._object, name)
            self._cache[name] = cw
            return cw
    
    def __init__(self, *args, **kwargs):
        super(ManagedObject, self).__init__(*args, **kwargs)
        self.scripts = ManagedObject.ScriptsProxy(self)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return site.reverse("sa:managedobject:change", self.id)
        
    @property
    def profile(self):
        """
        Get object's profile instance. Instances are cached. Same profile's
        instance will be returned for all .profile invocations for
        given managed objet
        
        :rtype: Profile instance
        """
        try:
            return self._cached_profile
        except AttributeError:
            self._cached_profile = profile_registry[self.profile_name]()
            return self._cached_profile
    
    @classmethod
    def user_objects(cls, user):
        """
        Get objects available to user
        
        :param user: User
        :type user: User instance
        :rtype: Queryset instance
        """
        return cls.objects.filter(UserAccess.Q(user))
    
    def has_access(self, user):
        """
        Check user has access to object
        
        :param user: User
        :type user: User instance
        :rtype: Bool
        """
        return self.user_objects(user).filter(id=self.id).exists()
    
    @property
    def granted_users(self):
        """
        Get list of user granted access to object

        :rtype: List of User instancies
        """
        return [u for u in User.objects.filter(is_active=True)
                if ManagedObject.objects.filter(UserAccess.Q(u) &
                                                Q(id=self.id)).exists()]
    
    @property
    def granted_groups(self):
        """
        Get list of groups granted access to object
        
        :rtype: List of Group instancies
        """
        return [g for g in Group.objects.filter()
                if ManagedObject.objects.filter(GroupAccess.Q(g) &
                                                Q(id=self.id)).exists()]
    
    def save(self):
        """
        Overload model's save()
        Change related Config object
        """
        # Get previous version
        if self.id:
            old = ManagedObject.objects.get(id=self.id)
        else:
            old = None
        # Save
        super(ManagedObject, self).save()
        # Notify changes
        if ((old is None and self.trap_source_ip) or
            (old and self.trap_source_ip != old.trap_source_ip) or
            (old and self.activator.id != old.activator.id)):
            sae_refresh_event_filter(self)
        # Process config
        try:
            # self.config is OneToOne field created by Config
            config = self.config 
        except:  # @todo: specify exact exception
            config = None
        if config is None: # No related Config object
            if self.is_configuration_managed:
                # Object is configuration managed, create related object
                from noc.cm.models import Config
                config = Config(managed_object=self,
                                repo_path=self.repo_path, pull_every=86400)
                config.save()
        else: # Update existing config entry when necessary
            if self.repo_path != self.config.repo_path:
                # Repo path has been changed
                config.repo_path = self.repo_path
            if self.is_configuration_managed and config.pull_every is None:
                # Device is configuration managed but not on periodic pull
                config.pull_every = 86400
            elif not self.is_configuration_managed and config.pull_every:
                # Reset pull_every for unmanaged devices
                config.pull_every = None
            config.save()
    
    def delete(self):
        """
        Delete related Config
        """
        from noc.cm.models import Config
        # Deny to delete "SAE" object
        if self.name == "SAE":
            raise IntegrityError("Cannot delete SAE object")
        try:
            if self.config.id:
                self.config.delete()
        except Config.DoesNotExist:
            pass
        super(ManagedObject, self).delete()
    
    @classmethod
    def search(cls, user, query, limit):
        """
        Search engine plugin
        """
        q = (Q(repo_path__icontains=query) |
             Q(name__icontains=query) |
             Q(address__icontains=query) |
             Q(user__icontains=query) |
             Q(description__icontains=query))
        for o in [o for o in cls.objects.filter(q) if o.has_access(user)]:
            relevancy = 1.0
            yield SearchResult(
                url=("sa:managedobject:change", o.id),
                title="SA: " + unicode(o),
                text=unicode(o),
                relevancy=relevancy)
    
    ##
    ## Returns True if Managed Object presents in more than one networks
    ##
    @property
    def is_router(self):
        return self.address_set.count() > 1
    
    ##
    ## Return attribute as string
    ##
    def get_attr(self, name, default=None):
        try:
            return self.managedobjectattribute_set.get(key=name).value
        except ManagedObjectAttribute.DoesNotExist:
            return default
    
    ##
    ## Return attribute as bool
    ##
    def get_attr_bool(self, name, default=False):
        v = self.get_attr(name)
        if v is None:
            return default
        if v.lower() in ["t", "true", "y", "yes", "1"]:
            return True
        else:
            return False
    
    ##
    ## Return attribute as integer
    ##
    def get_attr_int(self, name, default=0):
        v = self.get_attr(name)
        if v is None:
            return default
        try:
            return int(v)
        except:
            return default
    
    ##
    ## Set attribute
    ##
    def set_attr(self, name, value):
        value = unicode(value)
        try:
            v = self.managedobjectattribute_set.get(key=name)
            v.value = value
        except ManagedObjectAttribute.DoesNotExist:
            v = ManagedObjectAttribute(managed_object=self,
                                       key=name, value=value)
        v.save()

    @property
    def platform(self):
        """
        Return "vendor model" string from attributes
        """
        x = [self.get_attr("vendor"), self.get_attr("platform")]
        x = [a for a in x if a]
        if x:
            return " ".join(x)
        else:
            return None
    
    def is_ignored_interface(self, interface):
        interface = self.profile.convert_interface_name(interface)
        rx = self.get_attr("ignored_interfaces")
        if rx:
            return re.match(rx, interface) is not None
        return False


class ManagedObjectAttribute(models.Model):
    
    class Meta:
        verbose_name = _("Managed Object Attribute")
        verbose_name_plural = _("Managed Object Attributes")
        unique_together = [("managed_object", "key")]
        ordering = ["managed_object", "key"]
    
    managed_object = models.ForeignKey(ManagedObject,
            verbose_name=_("Managed Object"))
    key = models.CharField(_("Key"), max_length=64)
    value = models.CharField(_("Value"), max_length=4096,
            blank=True, null=True)
    
    def __unicode__(self):
        return u"%s: %s" % (self.managed_object, self.key)
    

##
## Object Selector
##
class ManagedObjectSelector(models.Model):
    
    class Meta:
        verbose_name = _("Managed Object Selector")
        verbose_name_plural = _("Managed Object Selectors")
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
    filter_user = models.CharField(_("Filter by User (REGEXP)"),
            max_length=256, null=True, blank=True)
    filter_remote_path = models.CharField(_("Filter by Remote Path (REGEXP)"),
            max_length=256, null=True, blank=True, validators=[check_re])
    filter_description = models.CharField(_("Filter by Description (REGEXP)"),
            max_length=256, null=True, blank=True, validators=[check_re])
    filter_repo_path = models.CharField(_("Filter by Repo Path (REGEXP)"),
            max_length=256, null=True, blank=True, validators=[check_re])
    filter_tags = AutoCompleteTagsField(_("Filter By Tags"),
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
        # @todo: Optimize with SQL
        t_ids = TaggedItem.objects.get_intersection_by_model(ManagedObject, self.filter_tags).values_list("id", flat=True)
        if t_ids:
            q &= Q(id__in=t_ids)
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
                o = ManagedObjectSelector.objects.get(name=so[1:])
                objects |= set(o.managed_objects)
            else:
                try:
                    o = ManagedObject.objects.get(id=int(so))
                except ValueError:
                    o = ManagedObject.objects.get(name=so)
                objects |= set([o])
        return list(objects)

##
## 
##
class ManagedObjectSelectorByAttribute(models.Model):
    
    class Meta:
        verbose_name = _("Managed Object Selector by Attribute")
        verbose_name = _("Managed Object Selectors by Attribute")
    
    selector = models.ForeignKey(ManagedObjectSelector,
            verbose_name=_("Object Selector"))
    key_re = models.CharField(_("Filter by key (REGEXP)"),
            max_length=256, validators=[check_re])
    value_re = models.CharField(_("Filter by value (REGEXP)"),
            max_length=256, validators=[check_re])
    
    def __unicode__(self):
        return u"%s: %s = %s" % (self.selector.name, self.key_re, self.value_re)
    

##
## Managed objects access for user
##
class UserAccess(models.Model):
    
    class Meta:
        verbose_name = _("User Access")
        verbose_name_plural = _("User Access")
        ordering = ["user"]  # @todo: sort by user__username
    
    user = models.ForeignKey(User, verbose_name=_("User"))
    selector = models.ForeignKey(ManagedObjectSelector,
            verbose_name=_("Object Selector"))
    
    def __unicode__(self):
        return u"(%s, %s)" % (self.user.username, self.selector.name)
    
    ##
    ## Return Q object for user access
    ##
    @classmethod
    def Q(cls, user):
        if user.is_superuser:
            return Q() # All objects
        # Build Q for user access
        uq = [a.selector.Q for a in UserAccess.objects.filter(user=user)]
        if uq:
            q = uq.pop(0)
            while uq:
                q |= uq.pop(0)
        else:
            q = Q(id__in=[]) # False
        # Enlarge with group access
        for gq in [GroupAccess.Q(g) for g in user.groups.all()]:
            q |= gq
        return q
    

##
## Managed objects access for group
##
class GroupAccess(models.Model):
    class Meta:
        verbose_name = _("Group Access")
        verbose_name_plural = _("Group Access")
        ordering = ["group"]  # @todo: Sort by group__name
    
    group = models.ForeignKey(Group, verbose_name=_("Group"))
    selector = models.ForeignKey(ManagedObjectSelector,
            verbose_name=_("Object Selector"))
    
    def __unicode__(self):
        return u"(%s, %s)" % (self.group.name, self.selector.name)
    
    ##
    ## Return Q object
    ##
    @classmethod
    def Q(cls, group):
        gq = [a.selector.Q for a in GroupAccess.objects.filter(group=group)]
        if gq:
            # Combine selectors
            q = gq.pop(0)
            while gq:
                q |= gq.pop(0)
            return q
        else:
            return Q(id__in=[]) # False
    

##
## Reduce Tasks
##
class ReduceTask(models.Model):
    
    class Meta:
        verbose_name = _("Map/Reduce Task")
        verbose_name_plural = _("Map/Reduce Tasks")
    start_time = models.DateTimeField(_("Start Time"))
    stop_time = models.DateTimeField(_("Stop Time"))
    script = models.TextField(_("Script"))
    script_params = PickledField(_("Params"), null=True, blank=True)
    
    class NotReady(Exception):
        pass
    
    def __unicode__(self):
        if self.id:
            return u"%d" % self.id
        else:
            return u"New: %s" % id(self)
    ##
    ##
    ##
    def save(self, **kwargs):
        if callable(self.script):
            # Make bootstrap from callable
            self.script = "import marshal,base64\n"\
            "@pyrule\n"\
            "def rule(*args,**kwargs): pass\n"\
            "rule.func_code=marshal.loads(base64.decodestring('%s'))\n" % (
                    base64.encodestring(marshal.dumps(self.script.func_code)).replace("\n", "\\n"))
        elif self.script.startswith("pyrule:"):
            # Reference to existing pyrule
            r = PyRule.objects.get(name=self.script[7:], interface="IReduceTask")
            self.script = r.text
        # Check syntax
        PyRule.compile_text(self.script)
        # Save
        super(ReduceTask, self).save(**kwargs)
    
    ##
    ## Check all map tasks are completed
    ##
    @property
    def complete(self):
        return self.stop_time <= datetime.datetime.now()\
            or (self.maptask_set.all().count() == self.maptask_set.filter(status__in=["C", "F"]).count())
    

    @classmethod
    def create_task(self, object_selector, reduce_script, reduce_script_params,
                    map_script, map_script_params, timeout=None):
        """
        Create Map/Reduce task

        :param object_selector: One of:
                                * ManagedObjectSelector instance
                                * List of ManagedObject instances or names
                                * ManagedObject's name
        :param reduce_script: One of:
                              * Function. ReduceTask will be passed as first
                                parameter
                              * PyRule
                              
        :param reduce_script_params: Reduce script parameters
        :type reduce_script_params: dict
        :param map_script: Script name either in form of Vendor.OS.script
                           or script
        :type map_script: str
        :param map_script_params: One of:
                                  
                                  * List of dicts or callables
                                  * Dict
        :type map_script_params: dict
        :param timeout: Task timeout, if None, timeout will be set
                        according to longest map task timeout
        :type timeout: Int or None
        :return: Task
        :rtype: ReduceTask
        """
        # Normalize map scripts to a list
        if type(map_script) in (types.ListType, types.TupleType):
            # list of map scripts
            map_script_list = map_script
            if type(map_script_params) in (types.ListType, types.TupleType):
                if len(map_script_params) != len(map_script):
                    raise Exception("Mismatched parameter list size")
                map_script_params_list = map_script_params
            else:
                # Expand to list
                map_script_params_list = [map_script_params] * len(map_script_list)
        else:
            # Single map script
            map_script_list = [map_script]
            map_script_params_list = [map_script_params]
        # Normalize a name of map scripts and join with parameters
        msp = []
        for ms, p in zip(map_script_list, map_script_params_list):
            s = ms.split(".")
            if len(s) == 3:
                ms = s[-1]
            elif len(s) != 1:
                raise Exception("Invalid map script: '%s'" % ms)
            msp += [(ms, p)]
        # Convert object_selector to a list of objects
        if type(object_selector) in (types.ListType, types.TupleType):
            objects = object_selector
        elif isinstance(object_selector, ManagedObjectSelector):
            objects = object_selector.managed_objects
        elif isinstance(object_selector, basestring):
            objects = [ManagedObject.objects.get(name=object_selector)]
        else:
            objects = list(object_selector)
        # Resolve strings to managed objects, if returned by selector
        objects = [ManagedObject.objects.get(name=x)
                   if isinstance(x, basestring) else x for x in objects]
        # Auto-detect reduce task timeout, if not set
        if not timeout:
            timeout = 0
            # Split timeouts to pools
            pool_timeouts = {}  # activator_id -> [timeouts]
            pc = {}  # Pool capabilities:  activator_id -> caps
            for o in objects:
                pool = o.activator.id
                ts = pool_timeouts.get(pool, [])
                if pool not in pc:
                    pc[pool] = o.activator.capabilities
                for ms, p in msp:
                    if ms not in o.profile.scripts:
                        continue
                    s = o.profile.scripts[ms]
                    ts += [s.TIMEOUT]
                pool_timeouts[pool] = ts
            # Calculate timeouts by pools
            for pool in pool_timeouts:
                t = 0
                # Get pool capacity
                c = pc[pool]
                if c["members"] > 0:
                    # Add timeouts by generations
                    ms = c["max_scripts"]
                    ts = sorted(pool_timeouts[pool])
                    if not ts:
                        continue
                    lts = len(ts) - 1
                    i = ms - 1
                    while True:
                        i = min(i, lts)
                        t += ts[i]
                        if i >= lts:
                            break
                        i += ms
                else:
                    # Give a try when cannot detect pool capabilities
                    t = max(pool_timeouts[pool])
                timeout = max(timeout, t)
            timeout += 3  # Add guard time
        # Use dumb reduce function if reduce task is none
        if reduce_script is None:
            reduce_script = reduce_dumb
        # Create reduce task
        start_time = datetime.datetime.now()
        r_task = ReduceTask(
            start_time=start_time,
            stop_time=start_time + datetime.timedelta(seconds=timeout),
            script=reduce_script,
            script_params=reduce_script_params if reduce_script_params else {},
        )
        r_task.save()
        # Caculate number of generations
        pc = {}  # Pool capabilities: activator id -> caps
        ngs = defaultdict(int)  # pool_id -> sessions requested
        for o in objects:
            n = len(msp)
            a_id = o.activator.id
            if a_id not in pc:
                pc[a_id] = o.activator.capabilities
            ngs[a_id] += n
        for p in ngs:
            ms = pc[p]["max_scripts"]
            if ms:
                ngs[p] = round(ngs[p] / ms + 0.5)
            else:
                ngs[p] = 0
        # Run map task for each object
        for o in objects:
            ng = ngs[o.activator.id]
            no_sessions = not ng and o.profile_name != "NOC.SAE"
            for ms, p in msp:
                # Set status to "F" if script not found
                if no_sessions or ms not in o.profile.scripts:
                    status = "F"
                else:
                    status = "W"
                # Build full map script name
                msn = "%s.%s" % (o.profile_name, ms)
                # Expand parameter, if callable
                if callable(p):
                    p = p(o)
                # Redistribute tasks
                if ng <= 1:
                    delay = 0
                else:
                    delay = random.randint(0, min(ng * 3, timeout / 2))
                #
                m = MapTask(
                    task=r_task,
                    managed_object=o,
                    map_script=msn,
                    script_params=p,
                    next_try=start_time + datetime.timedelta(seconds=delay),
                    status=status
                )
                if status == "F":
                    if no_sessions:
                        m.script_result = dict(code=ERR_ACTIVATOR_NOT_AVAILABLE,
                                               text="Activator pool is down")
                    else:
                        m.script_result = dict(code=ERR_INVALID_SCRIPT,
                                               text="Invalid script %s" % msn)
                m.save()
        return r_task
    
    ##
    ## Perform reduce script and execute result
    ##
    def reduce(self):
        return PyRule.compile_text(self.script)(self, **self.script_params)
    
    ##
    ## Get task result
    ##
    def get_result(self, block=True):
        while True:
            if self.complete:
                result = self.reduce()
                self.delete()
                return result
            else:
                if block:
                    time.sleep(3)
                else:
                    raise ReduceTask.NotReady
    
    ##
    ## Wait untill all task complete
    ##
    @classmethod
    def wait_for_tasks(cls, tasks):
        while tasks:
            time.sleep(3)
            rest = []
            for t in tasks:
                if t.complete:
                    t.reduce() # delete task and trigger reduce task
                    t.delete()
                else:
                    rest += [t]
                tasks = rest
    

##
## Map Tasks
##
class MapTask(models.Model):
    class Meta:
        verbose_name = _("Map/Reduce Task Data")
        verbose_name = _("Map/Reduce Task Data")
    task = models.ForeignKey(ReduceTask, verbose_name=_("Task"))
    managed_object = models.ForeignKey(ManagedObject,
            verbose_name=_("Managed Object"))
    map_script = models.CharField(_("Script"), max_length=256)
    script_params = PickledField(_("Params"), null=True, blank=True)
    next_try = models.DateTimeField(_("Next Try"))
    retries_left = models.IntegerField(_("Retries Left"), default=1)
    status = models.CharField(_("Status"), max_length=1,
            choices=[("W", _("Wait")), ("R", _("Running")),
                     ("C", _("Complete")), ("F", _("Failed"))], default="W")
    script_result = PickledField(_("Result"), null=True, blank=True)
    
    def __unicode__(self):
        if self.id:
            return u"%d: %s %s" % (self.id, self.managed_object,
                                   self.map_script)
        else:
            return u"New: %s %s" % (self.managed_object, self.map_script)
    

class CommandSnippet(models.Model):
    """
    Command snippet
    """
    class Meta:
        verbose_name = _("Command Snippet")
        verbose_name_plural = _("Command Snippets")
        ordering = ["name"]
    
    name = models.CharField(_("Name"), max_length = 128, unique = True)
    description = models.TextField(_("Description"))
    snippet = models.TextField(_("Snippet"),
            help_text=_("Code snippet template"))
    change_configuration = models.BooleanField(_("Change configuration"),
            default=False)
    selector = models.ForeignKey(ManagedObjectSelector,
                                 verbose_name=_("Object Selector"))
    is_enabled = models.BooleanField(_("Is Enabled?"), default=True)
    timeout = models.IntegerField(_("Timeout (sec)"), default=60)
    require_confirmation = models.BooleanField(_("Require Confirmation"),
            default=False)
    ignore_cli_errors = models.BooleanField(_("Ignore CLI errors"),
            default=False)
    # Restrict access to snippet if set
    # effective permission name will be sa:runsnippet:<permission_name>
    permission_name = models.CharField(_("Permission Name"), max_length=64,
                                       null=True, blank=True)
    display_in_menu = models.BooleanField(_("Show in menu"), default=False)
    #
    tags = AutoCompleteTagsField(_("Tags"), null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return site.reverse("sa:commandsnippet:change", self.id)
    
    rx_var = re.compile(r"{{\s*([^|}]+)\s*(?:\|.+?)?}}", re.MULTILINE)
    rx_vartag = re.compile(r"\{%\s*var\s+(?P<name>\S+)\s+(?P<type>\S+)\s*%\}",
                           re.MULTILINE)

    @property
    def vars(self):
        """
        List of variables used in template
        """
        internal = set()
        for match in self.rx_vartag.finditer(self.snippet):
            name, type = match.groups()
            if type == "internal":
                internal.add(name)
        return set([v for v in self.rx_var.findall(self.snippet)
                    if not v.startswith("object.") and v not in internal])

    def expand(self, data):
        """
        Expand snippet with variables
        """
        from django.template import Template, Context
        return Template(self.snippet).render(Context(data))

    @property
    def effective_permission_name(self):
        if self.permission_name:
            return "sa:runsnippet:" + self.permission_name
        else:
            return "sa:runsnippet:default"

    def save(self, *args, **kwargs):
        super(CommandSnippet, self).save(*args, **kwargs)
        # Create permission if required
        if self.permission_name:
            try:
                Permission.objects.get(name=self.effective_permission_name)
            except Permission.DoesNotExist:
                Permission(name=self.effective_permission_name).save()


class ActivatorCapabilitiesCache(nosql.Document):
    meta = {
        "collection": "noc.activatorcapscache",
        "allow_inheritance": False
    }

    activator_id = nosql.IntField()
    members = nosql.IntField()
    max_scripts = nosql.IntField()

    def __unicode__(self):
        return u"Activator Caps (%d)" % self.activator_id

    @classmethod
    def reset_cache(self, shards):
        """
        Reset caches for shards
        :param shard: List of shard names or ids
        """
        ids = set()
        for shard in shards:
            if isinstance(shard, basestring):
                s = Shard.objects.get(name=shard)
            else:
                s = Shard.objects.get(pk=shard)
            ids.union(set(s.activator_set.values_list("id", flat=True)))
        ActivatorCapabilitiesCache.objects(activator_id__in=ids).delete()


class MRTConfig(nosql.Document):
    meta = {
        "collection": "noc.mrtconfig",
        "allow_inheritance": False
    }
    name = nosql.StringField(unique=True)
    is_active = nosql.BooleanField(default=True)
    description = nosql.StringField(required=False)
    permission_name = nosql.StringField(required=True)
    selector = nosql.ForeignKeyField(ManagedObjectSelector, required=True)
    reduce_pyrule = nosql.ForeignKeyField(PyRule, required=True)
    map_script = nosql.StringField(required=True)
    timeout = nosql.IntField(required=False)

    def __unicode__(self):
        return self.name


##
## Reduce Scripts
##
def reduce_object_script(task):
    mt = task.maptask_set.all()[0]
    if mt.status == "C":
        return mt.script_result
    else:
        return None

def reduce_dumb(task):
    pass

##
## SAE services shortcuts
##
def sae_refresh_event_filter(object):
    """
    Refresh event filters for all activators serving object
    
    :param object: Managed object
    :type object: ManagedObject instance
    """
    def reduce_notify(task):
        mt = task.maptask_set.all()[0]
        if mt.status == "C":
            return mt.script_result
        return False
    
    t = ReduceTask.create_task("SAE", reduce_notify, {},
                               "notify", {"event": "refresh_event_filter",
                                          "object_id": object.id}, 1)
    #return t.get_result()
