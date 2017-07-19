# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ManagedObject
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import difflib
from collections import namedtuple
import logging
import os
import re
import itertools
import operator
from threading import Lock
# Third-party modules
from django.db.models import (Q, Model, CharField, BooleanField,
                              ForeignKey, IntegerField, FloatField,
                              DateTimeField, BigIntegerField, SET_NULL)
from django.contrib.auth.models import User, Group
import cachetools
import six
# NOC modules
from .administrativedomain import AdministrativeDomain
from .authprofile import AuthProfile
from .managedobjectprofile import ManagedObjectProfile
from .objectstatus import ObjectStatus
from .objectmap import ObjectMap
from .objectdata import ObjectData
from .terminationgroup import TerminationGroup
from noc.main.models.pool import Pool
from noc.main.models.timepattern import TimePattern
from noc.main.models import PyRule
from noc.main.models.notificationgroup import NotificationGroup
from noc.main.models.remotesystem import RemoteSystem
from noc.inv.models.networksegment import NetworkSegment
from noc.fm.models.ttsystem import TTSystem, DEFAULT_TTSYSTEM_SHARD
from noc.core.profile.loader import loader as profile_loader
from noc.core.model.fields import INETField, TagsField, DocumentReferenceField, CachedForeignKey
from noc.lib.db import SQL
from noc.lib.app.site import site
from noc.lib.stencil import stencil_registry
from noc.lib.validators import is_ipv4, is_ipv4_prefix
from noc.core.ip import IP
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.gridvcs.manager import GridVCSField
from noc.main.models.textindex import full_text_search, TextIndex
from noc.settings import config
from noc.core.scheduler.job import Job
from noc.core.handler import get_handler
from noc.core.debug import error_report
from noc.sa.mtmanager import MTManager
from noc.core.script.loader import loader as script_loader
from noc.core.model.decorator import on_save, on_init, on_delete, on_delete_check
from noc.inv.models.object import Object
from noc.core.defer import call_later
from noc.core.cache.decorator import cachedmethod
from noc.core.cache.base import cache
from noc.core.script.caller import SessionContext
from noc.core.bi.decorator import bi_sync

# Increase whenever new field added
MANAGEDOBJECT_CACHE_VERSION = 2

scheme_choices = [(1, "telnet"), (2, "ssh"), (3, "http"), (4, "https")]

Credentials = namedtuple("Credentials", [
    "user", "password", "super_password", "snmp_ro", "snmp_rw"])
Version = namedtuple("Version", ["profile", "vendor", "platform", "version"])

id_lock = Lock()

logger = logging.getLogger(__name__)


@full_text_search
@bi_sync
@on_init
@on_save
@on_delete
@on_delete_check(check=[
    # ("cm.ValidationRule.ObjectItem", ""),
    ("fm.ActiveAlarm", "managed_object"),
    ("fm.ActiveEvent", "managed_object"),
    ("fm.ArchivedAlarm", "managed_object"),
    ("fm.ArchivedEvent", "managed_object"),
    ("fm.FailedEvent", "managed_object"),
    ("fm.NewEvent", "managed_object"),
    ("inv.Interface", "managed_object"),
    ("inv.SubInterface", "managed_object")
    # ("maintainance.Maintainance", "escalate_managed_object"),
])
class ManagedObject(Model):
    """
    Managed Object
    """
    class Meta:
        verbose_name = "Managed Object"
        verbose_name_plural = "Managed Objects"
        db_table = "sa_managedobject"
        app_label = "sa"
        ordering = ["name"]

    name = CharField("Name", max_length=64, unique=True)
    is_managed = BooleanField("Is Managed?", default=True)
    container = DocumentReferenceField(
        Object, null=True, blank=True
    )
    administrative_domain = CachedForeignKey(
        AdministrativeDomain,
        verbose_name="Administrative Domain"
    )
    segment = DocumentReferenceField(
        NetworkSegment, null=False, blank=False
    )
    pool = DocumentReferenceField(
        Pool,
        null=False, blank=False
    )
    profile_name = CharField(
        "SA Profile",
        max_length=128, choices=profile_loader.choices()
    )
    object_profile = CachedForeignKey(
        ManagedObjectProfile,
        verbose_name="Object Profile")
    description = CharField(
        "Description",
        max_length=256, null=True, blank=True)
    # Access
    auth_profile = CachedForeignKey(
        AuthProfile,
        verbose_name="Auth Profile",
        null=True, blank=True
    )
    scheme = IntegerField(
        "Scheme", choices=scheme_choices
    )
    address = CharField("Address", max_length=64)
    port = IntegerField("Port", blank=True, null=True)
    user = CharField("User", max_length=32, blank=True, null=True)
    password = CharField(
        "Password",
        max_length=32, blank=True, null=True
    )
    super_password = CharField(
        "Super Password",
        max_length=32, blank=True, null=True
    )
    remote_path = CharField(
        "Path",
        max_length=256, blank=True, null=True
    )
    trap_source_type = CharField(
        max_length=1,
        choices=[
            ("d", "Disable"),
            ("m", "Management Address"),
            ("s", "Specify address"),
            ("l", "Loopback address"),
            ("a", "All interface addresses")
        ],
        default="d", null=False, blank=False
    )
    trap_source_ip = INETField(
        "Trap Source IP",
        null=True, blank=True, default=None
    )
    syslog_source_type = CharField(
        max_length=1,
        choices=[
            ("d", "Disable"),
            ("m", "Management Address"),
            ("s", "Specify address"),
            ("l", "Loopback address"),
            ("a", "All interface addresses")
        ],
        default="d", null=False, blank=False
    )
    syslog_source_ip = INETField(
        "Syslog Source IP",
        null=True, blank=True, default=None)
    trap_community = CharField(
        "Trap Community",
        blank=True, null=True, max_length=64
    )
    snmp_ro = CharField(
        "RO Community",
        blank=True, null=True, max_length=64
    )
    snmp_rw = CharField(
        "RW Community",
        blank=True, null=True, max_length=64
    )
    #
    vc_domain = ForeignKey(
        "vc.VCDomain",
        verbose_name="VC Domain",
        null=True, blank=True
    )
    # CM
    config = GridVCSField("config", mirror=config.path.config_mirror_path)
    # Default VRF
    vrf = ForeignKey("ip.VRF", verbose_name="VRF",
                            blank=True, null=True)
    # Reference to controller, when object is CPE
    controller = ForeignKey(
        "self", verbose_name="Controller",
        blank=True, null=True
    )
    # CPE id on given controller
    local_cpe_id = CharField(
        "Local CPE ID",
        max_length=128,
        null=True, blank=True
    )
    # Globally unique CPE id
    global_cpe_id = CharField(
        "Global CPE ID",
        max_length=128,
        null=True, blank=True
    )
    # Last seen date, for CPE
    last_seen = DateTimeField(
        "Last Seen",
        blank=True, null=True
    )
    # For service terminators
    # Name of service termination group (i.e. BRAS, SBC)
    termination_group = ForeignKey(
        TerminationGroup, verbose_name="Termination Group",
        blank=True, null=True,
        related_name="termination_set"
    )
    # For access switches -- L3 terminator
    service_terminator = ForeignKey(
        TerminationGroup, verbose_name="Service termination",
        blank=True, null=True,
        related_name="access_set"
    )
    # Stencils
    shape = CharField("Shape", blank=True, null=True,
        choices=stencil_registry.choices, max_length=128)
    #
    time_pattern = ForeignKey(
        TimePattern,
        null=True, blank=True,
        on_delete=SET_NULL
    )
    # pyRules
    config_filter_rule = ForeignKey(
        PyRule,
        verbose_name="Config Filter pyRule",
        limit_choices_to={"interface": "IConfigFilter"},
        null=True, blank=True,
        on_delete=SET_NULL,
        related_name="managed_object_config_filter_rule_set")
    config_diff_filter_rule = ForeignKey(
        PyRule,
        verbose_name="Config Diff Filter Rule",
        limit_choices_to={"interface": "IConfigDiffFilter"},
        null=True, blank=True,
        on_delete=SET_NULL,
        related_name="managed_object_config_diff_rule_set")
    config_validation_rule = ForeignKey(
        PyRule,
        verbose_name="Config Validation pyRule",
        limit_choices_to={"interface": "IConfigValidator"},
        null=True, blank=True,
        on_delete=SET_NULL,
        related_name="managed_object_config_validation_rule_set")
    max_scripts = IntegerField(
        "Max. Scripts",
        null=True, blank=True,
        help_text="Concurrent script session limits")
    # Latitude and longitude, copied from container
    x = FloatField(null=True, blank=True)
    y = FloatField(null=True, blank=True)
    default_zoom = IntegerField(null=True, blank=True)
    # Integration with external NRI and TT systems
    # Reference to remote system object has been imported from
    remote_system = DocumentReferenceField(RemoteSystem,
                                           null=True, blank=True)
    # Object id in remote system
    remote_id = CharField(max_length=64, null=True, blank=True)
    # Object id in BI
    bi_id = BigIntegerField(null=True, blank=True)
    # Object alarms can be escalated
    escalation_policy = CharField(
        "Escalation Policy",
        max_length=1,
        choices=[
            ("E", "Enable"),
            ("D", "Disable"),
            ("P", "From Profile")
        ],
        default="P"
    )
    # Raise alarms on discovery problems
    box_discovery_alarm_policy = CharField(
        "Box Discovery Alarm Policy",
        max_length=1,
        choices=[
            ("E", "Enable"),
            ("D", "Disable"),
            ("P", "From Profile")
        ],
        default="P"
    )
    periodic_discovery_alarm_policy = CharField(
        "Box Discovery Alarm Policy",
        max_length=1,
        choices=[
            ("E", "Enable"),
            ("D", "Disable"),
            ("P", "From Profile")
        ],
        default="P"
    )
    # TT system for this object
    tt_system = DocumentReferenceField(TTSystem,
                                       null=True, blank=True)
    # TT system queue for this object
    tt_queue = CharField(max_length=64, null=True, blank=True)
    # Object id in tt system
    tt_system_id = CharField(max_length=64, null=True, blank=True)
    #
    tags = TagsField("Tags", null=True, blank=True)

    # Use special filter for profile
    profile_name.existing_choices_filter = True

    # Event ids
    EV_CONFIG_CHANGED = "config_changed"  # Object's config changed
    EV_ALARM_RISEN = "alarm_risen"  # New alarm risen
    EV_ALARM_REOPENED = "alarm_reopened"  # Alarm has been reopen
    EV_ALARM_CLEARED = "alarm_cleared"  # Alarm cleared
    EV_ALARM_COMMENTED = "alarm_commented"  # Alarm commented
    EV_NEW = "new"  # New object created
    EV_DELETED = "deleted"  # Object deleted
    EV_VERSION_CHANGED = "version_changed"  # Version changed
    EV_INTERFACE_CHANGED = "interface_changed"  # Interface configuration changed
    EV_SCRIPT_FAILED = "script_failed"  # Script error
    EV_CONFIG_POLICY_VIOLATION = "config_policy_violation"  # Policy violations found

    PROFILE_LINK = "object_profile"

    BOX_DISCOVERY_JOB = "noc.services.discovery.jobs.box.job.BoxDiscoveryJob"
    PERIODIC_DISCOVERY_JOB = "noc.services.discovery.jobs.periodic.job.PeriodicDiscoveryJob"

    _id_cache = cachetools.TTLCache(maxsize=1000, ttl=60)

    def __unicode__(self):
        return self.name

    @classmethod
    @cachedmethod(operator.attrgetter("_id_cache"),
                  key="managedobject-id-%s",
                  lock=lambda _: id_lock,
                  version=MANAGEDOBJECT_CACHE_VERSION)
    def get_by_id(cls, id):
        mo = ManagedObject.objects.filter(id=id)[:1]
        if mo:
            return mo[0]
        else:
            return None

    @property
    def data(self):
        try:
            return self._data
        except AttributeError:
            pass
        d = ObjectData.get_by_id(self)
        if not d:
            d = ObjectData(object=self.id)
        self._data = d
        return d

    @property
    def scripts(self):
        sp = getattr(self, "_scripts", None)
        if sp:
            return sp
        else:
            self._scripts = ScriptsProxy(self)
            return self._scripts

    @property
    def actions(self):
        return ActionsProxy(self)

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
        cp = getattr(self, "_cached_profile", None)
        if not cp:
            cp = profile_loader.get_profile(self.profile_name)()
            self._cached_profile = cp
        return cp

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
        if user.is_superuser:
            return True
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

    def on_save(self):
        # Invalidate caches
        deleted_cache_keys = [
            "managedobject-name-to-id-%s" % self.name
        ]
        # IPAM sync
        if self.object_profile.sync_ipam:
            self.sync_ipam()
        # Notify new object
        if not self.initial_data["id"]:
            self.event(self.EV_NEW, {"object": self})
        # Remove discovery jobs from old pool
        if "pool" in self.changed_fields and self.initial_data["id"]:
            pool_name = Pool.get_by_id(self.initial_data["pool"]).name
            Job.remove(
                "discovery",
                self.BOX_DISCOVERY_JOB,
                key=self.id,
                pool=pool_name
            )
            Job.remove(
                "discovery",
                self.PERIODIC_DISCOVERY_JOB,
                key=self.id,
                pool=pool_name
            )
        # Rebuild object maps
        if (
            self.initial_data["id"] is None or
            "is_managed" in self.changed_fields or
            "object_profile" in self.changed_fields or
            "trap_source_type" in self.changed_fields or
            "trap_source_ip" in self.changed_fields or
            "syslog_source_type" in self.changed_fields or
            "syslog_source_ip" in self.changed_fields or
            "address" in self.changed_fields or
            "pool" in self.changed_fields or
            "time_pattern" in self.changed_fields
        ):
            ObjectMap.invalidate(self.pool)
        # Invalidate credentials cache
        if (
            self.initial_data["id"] is None or
            "scheme" in self.changed_fields or
            "address" in self.changed_fields or
            "port" in self.changed_fields or
            "auth_profile" in self.changed_fields or
            "user" in self.changed_fields or
            "password" in self.changed_fields or
            "super_password" in self.changed_fields or
            "snmp_ro" in self.changed_fields or
            "snmp_rw" in self.changed_fields or
            "profile_name" in self.changed_fields or
            "pool" in self.changed_fields
        ):
            deleted_cache_keys += ["cred-%s" % self.id]
            if "profile_name" in self.changed_fields:
                self.reset_platform()
        # Rebuild paths
        if (
            self.initial_data["id"] is None or
            "administrative_domain" in self.changed_fields or
            "segment" in self.changed_fields or
            "container" in self.changed_fields
        ):
            ObjectData.refresh_path(self)
            if self.container and "container" in self.changed_fields:
                x, y, zoom = self.container.get_coordinates_zoom()
                ManagedObject.objects.filter(id=self.id).update(
                    x=x,
                    y=y,
                    default_zoom=zoom
                )
        if self.initial_data["id"] and "container" in self.changed_fields:
            # Move object to another container
            if self.container:
                for o in Object.get_managed(self):
                    o.container = self.container.id
                    o.log("Moved to container %s (%s)" % (self.container, self.container.id))
                    o.save()
        # Rebuild summary
        if "object_profile" in self.changed_fields:
            self.segment.update_summary()
        # Rebuild segment access
        if self.initial_data["id"] is None:
            self.segment.update_access()
        elif "segment" in self.changed_fields:
            iseg = self.initial_data["segment"]
            if iseg and isinstance(iseg, six.string_types):
                iseg = NetworkSegment.get_by_id(iseg)
            if iseg:
                iseg.update_access()
                iseg.update_uplinks()
            self.segment.update_access()
            self.update_topology()
        # Apply discovery jobs
        self.ensure_discovery_jobs()
        # Rebuild selector cache
        SelectorCache.rebuild_for_object(self)
        #
        cache.delete("managedobject-id-%s" % self.id,
                     version=MANAGEDOBJECT_CACHE_VERSION)
        cache.delete_many(deleted_cache_keys)
        # Handle became unmanaged
        if (
            not self.initial_data["id"] is None and
            "is_managed" in self.changed_fields and
            not self.is_managed
        ):
            # Clear alarms
            from noc.fm.models.activealarm import ActiveAlarm
            for aa in ActiveAlarm.objects.filter(managed_object=self.id):
                aa.clear_alarm("Management is disabled")
            # Clear discovery id
            from noc.inv.models.discoveryid import DiscoveryID
            DiscoveryID.clean_for_object(self)

    def on_delete(self):
        # Rebuild selector cache
        SelectorCache.refresh()
        # Reset discovery cache
        from noc.inv.models.discoveryid import DiscoveryID
        DiscoveryID.clean_for_object(self)

    def sync_ipam(self):
        """
        Synchronize FQDN and address with IPAM
        """
        from noc.ip.models.address import Address
        from noc.ip.models.vrf import VRF
        # Generate FQDN from template
        fqdn = self.object_profile.get_fqdn(self)
        # Get existing IPAM record
        vrf = self.vrf if self.vrf else VRF.get_global()
        try:
            a = Address.objects.get(vrf=vrf, address=self.address)
        except Address.DoesNotExist:
            # Create new address
            Address(
                vrf=vrf,
                address=self.address,
                fqdn=fqdn,
                managed_object=self
            ).save()
            return
        # Update existing address
        if (a.managed_object != self or
            a.address != self.address or a.fqdn != fqdn):
            a.managed_object = self
            a.address = self.address
            a.fqdn = fqdn
            a.save()

    def get_index(self):
        """
        Get FTS index
        """
        card = "Managed object %s (%s)" % (self.name, self.address)
        content = [
            self.name,
            self.address,
        ]
        if self.trap_source_ip:
            content += [self.trap_source_ip]
        platform = self.platform
        if platform:
            content += [platform]
            card += " [%s]" % platform
        version = self.get_attr("version")
        if version:
            content += [version]
            card += " version %s" % version
        if self.description:
            content += [self.description]
        config = self.config.read()
        if config:
            if len(config) > 10000000:
                content += [config[:10000000]]
            else:
                content += [config]
        r = {
            "title": self.name,
            "content": "\n".join(content),
            "card": card,
            "tags": self.tags
        }
        return r

    @property
    def is_router(self):
        """
        Returns True if Managed Object presents in more than one networks
        :return:
        """
        # @todo: Rewrite
        return self.address_set.count() > 1

    def get_attr(self, name, default=None):
        """
        Return attribute as string
        :param name:
        :param default:
        :return:
        """
        try:
            return self.managedobjectattribute_set.get(key=name).value
        except ManagedObjectAttribute.DoesNotExist:
            return default

    def get_attr_bool(self, name, default=False):
        """
        Return attribute as bool
        :param name:
        :param default:
        :return:
        """
        v = self.get_attr(name)
        if v is None:
            return default
        if v.lower() in ["t", "true", "y", "yes", "1"]:
            return True
        else:
            return False

    def get_attr_int(self, name, default=0):
        """
        Return attribute as integer
        :param name:
        :param default:
        :return:
        """
        v = self.get_attr(name)
        if v is None:
            return default
        try:
            return int(v)
        except:
            return default

    def set_attr(self, name, value):
        """
        Set attribute
        :param name:
        :param value:
        :return:
        """
        value = unicode(value)
        try:
            v = self.managedobjectattribute_set.get(key=name)
            v.value = value
        except ManagedObjectAttribute.DoesNotExist:
            v = ManagedObjectAttribute(managed_object=self,
                                       key=name, value=value)
        v.save()

    def reset_platform(self):
        """
        Reset platform and version information
        """
        self.managedobjectattribute_set.filter(
            key__in=["vendor", "platform", "version"]
        ).delete()

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

    @property
    def vendor(self):
        return self.get_attr("vendor")

    def is_ignored_interface(self, interface):
        interface = self.profile.convert_interface_name(interface)
        rx = self.get_attr("ignored_interfaces")
        if rx:
            return re.match(rx, interface) is not None
        return False

    def get_status(self):
        return ObjectStatus.get_status(self)

    def get_last_status(self):
        return ObjectStatus.get_last_status(self)

    def set_status(self, status, ts=None):
        """
        Update managed object status
        :param status: new status
        :param ts: status change time
        :return: False if out-of-order update, True otherwise
        """
        return ObjectStatus.set_status(self, status, ts=ts)

    def get_inventory(self):
        """
        Retuns a list of inventory Objects managed by
        this managed object
        """
        from noc.inv.models.object import Object
        return list(Object.objects.filter(
            data__management__managed_object=self.id))

    def run_discovery(self, delta=0):
        """
        Schedule box discovery
        """
        if not self.object_profile.enable_box_discovery or not self.is_managed:
            return
        logger.debug("[%s] Scheduling box discovery after %ds",
                     self.name, delta)
        Job.submit(
            "discovery",
            self.BOX_DISCOVERY_JOB,
            key=self.id,
            pool=self.pool.name,
            delta=delta or self.pool.get_delta()
        )

    def event(self, event_id, data=None, delay=None, tag=None):
        """
        Process object-related event
        :param event_id: ManagedObject.EV_*
        :param data: Event context to render
        :param delay: Notification delay in seconds
        :param tag: Notification tag
        """
        # Get cached selectors
        selectors = SelectorCache.get_object_selectors(self)
        # Find notification groups
        groups = set()
        for o in ObjectNotification.objects.filter(**{
                event_id: True,
                "selector__in": selectors
        }):
            groups.add(o.notification_group)
        if not groups:
            return  # Nothing to notify
        # Render message
        subject, body = ObjectNotification.render_message(event_id, data)
        # Send notification
        if not tag and event_id in (
                self.EV_ALARM_CLEARED,
                self.EV_ALARM_COMMENTED,
                self.EV_ALARM_REOPENED,
                self.EV_ALARM_RISEN) and "alarm" in data:
            tag = "alarm:%s" % data["alarm"].id
        NotificationGroup.group_notify(
            groups, subject=subject, body=body, delay=delay, tag=tag)
        # Schedule FTS reindex
        if event_id in (
            self.EV_CONFIG_CHANGED, self.EV_VERSION_CHANGED):
            TextIndex.update_index(ManagedObject, self)

    def save_config(self, data):
        if isinstance(data, list):
            # Convert list to plain text
            r = []
            for d in sorted(data, lambda x, y: cmp(x["name"], y["name"])):
                r += ["==[ %s ]========================================\n%s" % (d["name"], d["config"])]
            data = "\n".join(r)
        # Pass data through config filter, if given
        if self.config_filter_rule:
            data = self.config_filter_rule(
                managed_object=self, config=data)
        # Pass data through the validation filter, if given
        # @todo: Remove
        if self.config_validation_rule:
            warnings = self.config_validation_rule(
                managed_object=self, config=data)
            if warnings:
                # There are some warnings. Notify responsible persons
                self.event(
                    self.EV_CONFIG_POLICY_VIOLATION,
                    {
                        "object": self,
                        "warnings": warnings
                    }
                )
        # Calculate diff
        old_data = self.config.read()
        is_new = not bool(old_data)
        diff = None
        if not is_new:
            # Calculate diff
            if self.config_diff_filter_rule:
                # Pass through filters
                old_data = self.config_diff_filter_rule(
                    managed_object=self, config=old_data)
                new_data = self.config_diff_filter_rule(
                    managed_object=self, config=data)
                if not old_data and not new_data:
                    logger.error("[%s] broken config_diff_filter: Returns empty result", self.name)
            else:
                new_data = data
            if old_data == new_data:
                return  # Nothing changed
            diff = "".join(difflib.unified_diff(
                old_data.splitlines(True),
                new_data.splitlines(True),
                fromfile=os.path.join("a", self.name.encode("utf8")),
                tofile=os.path.join("b", self.name.encode("utf8"))
            ))
        # Notify changes
        self.event(
            self.EV_CONFIG_CHANGED,
            {
                "object": self,
                "is_new": is_new,
                "config": data,
                "diff": diff
            }
        )
        # Save config
        self.config.write(data)
        # Run config validation
        from noc.cm.engine import Engine
        engine = Engine(self)
        try:
            engine.check()
        except:
            logger.error("Failed to validate config for %s", self.name)
            error_report()

    @property
    def credentials(self):
        """
        Get effective credentials
        """
        if self.auth_profile:
            return Credentials(
                user=self.auth_profile.user,
                password=self.auth_profile.password,
                super_password=self.auth_profile.super_password,
                snmp_ro=self.auth_profile.snmp_ro or self.snmp_ro,
                snmp_rw=self.auth_profile.snmp_rw or self.snmp_rw
            )
        else:
            return Credentials(
                user=self.user,
                password=self.password,
                super_password=self.super_password,
                snmp_ro=self.snmp_ro,
                snmp_rw=self.snmp_rw
            )

    @property
    def scripts_limit(self):
        ol = self.max_scripts or None
        pl = self.profile.max_scripts
        if not ol:
            return pl
        if pl:
            return min(ol, pl)
        else:
            return ol

    def iter_recursive_objects(self):
        """
        Generator yilding all recursive objects
        for effective PM settings
        """
        from noc.inv.models.interface import Interface
        for i in Interface.objects.filter(managed_object=self.id):
            yield i

    def get_caps(self):
        """
        Returns a dict of effective object capabilities
        """
        return ObjectCapabilities.get_capabilities(self)

    def update_caps(self, caps, source):
        """
        Update existing capabilities with a new ones.
        :param caps: dict of caps name -> caps value
        :param source: Source name
        """
        return ObjectCapabilities.update_capabilities(self, caps, source)

    def disable_discovery(self):
        """
        Disable all discovery methods related with managed object
        """

    @property
    def version(self):
        """
        Returns filled Version object
        """
        if not hasattr(self, "_c_version"):
            self._c_version = Version(
                profile=self.profile_name,
                vendor=self.get_attr("vendor"),
                platform=self.get_attr("platform"),
                version=self.get_attr("version")
            )
        return self._c_version

    def get_parser(self):
        """
        Return parser instance or None.
        Depends on version_discovery
        """
        v = self.version
        cls = self.profile.get_parser(v.vendor, v.platform, v.version)
        if cls:
            return get_handler(cls)(self)
        else:
            return get_handler("noc.cm.parsers.base.BaseParser")(self)

    def get_interface(self, name):
        from noc.inv.models.interface import Interface

        name = self.profile.convert_interface_name(name)
        try:
            return Interface.objects.get(managed_object=self.id, name=name)
        except Interface.DoesNotExist:
            pass
        for n in self.profile.get_interface_names(name):
            try:
                return Interface.objects.get(managed_object=self.id, name=n)
            except Interface.DoesNotExist:
                pass
        return None

    def ensure_discovery_jobs(self):
        """
        Check and schedule discovery jobs
        """
        if self.is_managed and self.object_profile.enable_box_discovery:
            Job.submit(
                "discovery",
                self.BOX_DISCOVERY_JOB,
                key=self.id,
                pool=self.pool.name,
                delta=self.pool.get_delta(),
                keep_ts=True
            )
        else:
            Job.remove(
                "discovery",
                self.BOX_DISCOVERY_JOB,
                key=self.id,
                pool=self.pool.name
            )
        if self.is_managed and self.object_profile.enable_periodic_discovery:
            Job.submit(
                "discovery",
                self.PERIODIC_DISCOVERY_JOB,
                key=self.id,
                pool=self.pool.name,
                delta=self.pool.get_delta(),
                keep_ts=True
            )
        else:
            Job.remove(
                "discovery",
                self.PERIODIC_DISCOVERY_JOB,
                key=self.id,
                pool=self.pool.name
            )

    def update_topology(self):
        """
        Rebuild topology caches
        """
        self.segment.update_uplinks()
        # Rebuild PoP links
        container = self.container
        for o in Object.get_managed(self):
            pop = o.get_pop()
            if not pop and container:
                # Fallback to MO container
                pop = container.get_pop()
            if pop:
                call_later(
                    "noc.inv.util.pop_links.update_pop_links",
                    20,
                    pop_id=pop.id
                )

    @classmethod
    def get_search_Q(cls, query):
        """
        Filters type:
        #1 IP address regexp - if .* in query
        #2 Name regexp - if "+*[]()" in query
        #3 IPv4 query - if query is valid IPv4 address
        #4 IPv4 prefix - if query is valid prefix from /16 to /32 (192.168.0.0/16, 192.168.0.0/g, 192.168.0.0/-1)
        #5 Discovery ID query - Find on MAC Discovery ID
        :param query: Query from __query request field
        :return: Django Q filter (Use it: ManagedObject.objects.filter(q))
        """
        query = query.strip()
        if query:
            if ".*" in query and is_ipv4(query.replace(".*", ".1")):
                return Q(address__regex=query.replace(".", "\\.")
                         .replace("*", "[0-9]+"))
            elif set("+*[]()") & set(query):
                # Maybe regular expression
                try:
                    # Check syntax
                    # @todo: PostgreSQL syntax differs from python one
                    re.compile(query)
                    return Q(name__regex=query)
                except re.error:
                    pass
            elif is_ipv4(query):
                # Exact match on IP address
                return Q(address=query)
            elif is_ipv4_prefix(query):
                # Match by prefix
                p = IP.prefix(query)
                return SQL("cast_test_to_inet(address) <<= '%s'" % p)
            else:
                try:
                    mac = MACAddressParameter().clean(query)
                    from noc.inv.models.discoveryid import DiscoveryID
                    mo = DiscoveryID.find_object(mac)
                    if mo:
                        return Q(pk=mo.pk)
                except ValueError:
                    pass
        return None

    def open_session(self, idle_timeout=None):
        return SessionContext(self, idle_timeout)

    def can_escalate(self):
        """
        Check alarm can be escalated
        :return:
        """
        if not self.tt_system or not self.tt_system_id:
            return False
        if self.escalation_policy == "E":
            return True
        elif self.escalation_policy == "P":
            return self.object_profile.can_escalate()
        else:
            return False

    def can_create_box_alarms(self):
        if self.box_discovery_alarm_policy == "E":
            return True
        elif self.box_discovery_alarm_policy == "P":
            return self.object_profile.can_create_box_alarms()
        else:
            return False

    def can_create_periodic_alarms(self):
        if self.periodic_discovery_alarm_policy == "E":
            return True
        elif self.periodic_discovery_alarm_policy == "P":
            return self.object_profile.can_create_periodic_alarms()
        else:
            return False

    @property
    def management_vlan(self):
        """
        Return management vlan settings
        :return: Vlan id or None
        """
        if self.segment.management_vlan_policy == "d":
            return None
        elif self.segment.management_vlan_policy == "e":
            return self.segment.management_vlan
        else:
            return self.segment.profile.management_vlan

    @property
    def multicast_vlan(self):
        """
        Return multicast vlan settings
        :return: Vlan id or None
        """
        if self.segment.multicast_vlan_policy == "d":
            return None
        elif self.segment.multicast_vlan_policy == "e":
            return self.segment.multicast_vlan
        else:
            return self.segment.profile.multicast_vlan

    @property
    def escalator_shard(self):
        """
        Returns escalator shard name
        :return:
        """
        if self.tt_system:
            return self.tt_system.shard_name
        else:
            return DEFAULT_TTSYSTEM_SHARD

@on_save
class ManagedObjectAttribute(Model):

    class Meta:
        verbose_name = "Managed Object Attribute"
        verbose_name_plural = "Managed Object Attributes"
        db_table = "sa_managedobjectattribute"
        app_label = "sa"
        unique_together = [("managed_object", "key")]
        ordering = ["managed_object", "key"]

    managed_object = ForeignKey(ManagedObject,
            verbose_name="Managed Object")
    key = CharField("Key", max_length=64)
    value = CharField("Value", max_length=4096,
            blank=True, null=True)

    def __unicode__(self):
        return u"%s: %s" % (self.managed_object, self.key)

    def on_save(self):
        cache.delete("cred-%s" % self.managed_object.id)


# object.scripts. ...
class ScriptsProxy(object):
    class CallWrapper(object):
        def __init__(self, obj, name):
            self.name = name
            self.object = obj

        def __call__(self, **kwargs):
            return MTManager.run(self.object, self.name, kwargs)

    def __init__(self, obj):
        self._object = obj
        self._cache = {}

    def __getattr__(self, name):
        if name in self._cache:
            return self._cache[name]
        if not script_loader.has_script("%s.%s" % (
                self._object.profile_name, name)):
            raise AttributeError("Invalid script %s" % name)
        cw = ScriptsProxy.CallWrapper(self._object, name)
        self._cache[name] = cw
        return cw

    def __getitem__(self, item):
        return getattr(self, item)

    def __contains__(self, item):
        """
        Check object has script name
        """
        if "." not in item:
            # Normalize to full name
            item = "%s.%s" % (self._object.profile_name, item)
        return script_loader.has_script(item)

    def __iter__(self):
        return itertools.imap(
                lambda y: y.split(".")[-1],
                itertools.ifilter(
                        lambda x: x.startswith(self._object.profile_name + "."),
                        script_loader.iter_scripts()
                )
        )


class ActionsProxy(object):
    class CallWrapper(object):
        def __init__(self, obj, name, action):
            self.name = name
            self.object = obj
            self.action = action

        def __call__(self, **kwargs):
            return self.action.execute(self.object, **kwargs)

    def __init__(self, obj):
        self._object = obj
        self._cache = {}

    def __getattr__(self, name):
        if name in self._cache:
            return self._cache[name]
        a = Action.objects.filter(name=name).first()
        if not a:
            raise AttributeError(name)
        cw = ActionsProxy.CallWrapper(self._object, name, a)
        self._cache[name] = cw
        return cw

# Avoid circular references
from .useraccess import UserAccess
from .groupaccess import GroupAccess
from .objectnotification import ObjectNotification
from .action import Action
from .selectorcache import SelectorCache
from .objectcapabilities import ObjectCapabilities
