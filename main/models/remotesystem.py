# ----------------------------------------------------------------------
# RemoteSystem model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from threading import Lock
import operator
import datetime
from typing import Optional, Union

# Third-party modules
import bson
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (
    StringField,
    ListField,
    EmbeddedDocumentField,
    BooleanField,
    DateTimeField,
    LongField,
)
import cachetools

# NOC modules
from noc.core.model.decorator import on_delete_check
from noc.core.handler import get_handler
from noc.core.bi.decorator import bi_sync
from noc.core.debug import error_report

id_lock = Lock()


class EnvItem(EmbeddedDocument):
    """
    Environment item
    """

    key = StringField()
    value = StringField()

    def __str__(self):
        return self.key


@bi_sync
@on_delete_check(
    check=[
        ("crm.Subscriber", "remote_system"),
        ("crm.SubscriberProfile", "remote_system"),
        ("crm.Supplier", "remote_system"),
        ("crm.SupplierProfile", "remote_system"),
        ("inv.ExtNRILink", "remote_system"),
        ("fm.ActiveAlarm", "remote_system"),
        ("fm.ArchivedAlarm", "remote_system"),
        ("fm.TTSystem", "remote_system"),
        ("gis.Address", "remote_system"),
        ("gis.Building", "remote_system"),
        ("gis.Division", "remote_system"),
        ("gis.Street", "remote_system"),
        ("inv.AllocationGroup", "remote_system"),
        ("inv.InterfaceProfile", "remote_system"),
        ("inv.NetworkSegment", "remote_system"),
        ("inv.NetworkSegmentProfile", "remote_system"),
        ("inv.ResourceGroup", "remote_system"),
        ("inv.Sensor", "remote_system"),
        ("inv.Object", "remote_system"),
        ("ip.VRF", "remote_system"),
        ("ip.AddressProfile", "remote_system"),
        ("ip.Address", "remote_system"),
        ("ip.PrefixProfile", "remote_system"),
        ("ip.Prefix", "remote_system"),
        ("main.Label", "remote_system"),
        ("main.NotificationGroupUserSubscription", "remote_system"),
        ("sa.ManagedObject", "remote_system"),
        ("sa.AdministrativeDomain", "remote_system"),
        ("sa.ManagedObjectProfile", "remote_system"),
        ("sa.AuthProfile", "remote_system"),
        ("sa.ServiceProfile", "remote_system"),
        ("inv.Channel", "remote_system"),
        ("inv.ResourceGroup", "remote_system"),
        ("sa.Service", "remote_system"),
        ("vc.VLAN", "remote_system"),
        ("vc.VLANProfile", "remote_system"),
        ("vc.VPN", "remote_system"),
        ("vc.VPNProfile", "remote_system"),
        ("vc.L2Domain", "remote_system"),
        ("vc.L2DomainProfile", "remote_system"),
        ("wf.State", "remote_system"),
        ("wf.Transition", "remote_system"),
        ("wf.Workflow", "remote_system"),
        ("project.Project", "remote_system"),
    ]
)
class RemoteSystem(Document):
    meta = {"collection": "noc.remotesystem", "strict": False, "auto_create_index": False}

    name = StringField(unique=True)
    description = StringField()
    handler = StringField()
    # Environment variables
    environment = ListField(EmbeddedDocumentField(EnvItem))
    # Enable extractors/loaders
    enable_address = BooleanField()
    enable_admdiv = BooleanField()
    enable_administrativedomain = BooleanField()
    enable_authprofile = BooleanField()
    enable_building = BooleanField()
    enable_container = BooleanField()
    enable_link = BooleanField()
    enable_managedobject = BooleanField()
    enable_managedobjectprofile = BooleanField()
    enable_networksegment = BooleanField()
    enable_networksegmentprofile = BooleanField()
    enable_object = BooleanField()
    enable_sensor = BooleanField()
    enable_service = BooleanField()
    enable_serviceprofile = BooleanField()
    enable_street = BooleanField()
    enable_subscriber = BooleanField()
    enable_subscriberprofile = BooleanField()
    enable_resourcegroup = BooleanField()
    enable_ttsystem = BooleanField()
    enable_project = BooleanField()
    enable_l2domain = BooleanField()
    enable_ipvrf = BooleanField()
    enable_ipprefix = BooleanField()
    enable_ipprefixprofile = BooleanField()
    enable_ipaddress = BooleanField()
    enable_ipaddressprofile = BooleanField()
    enable_label = BooleanField()
    enable_discoveredobject = BooleanField()
    enable_fmevent = BooleanField()
    managed_object_loader_policy = StringField(
        choices=[("D", "As Discovered"), ("M", "As Managed Object")],
        default="M",
    )
    # Usage statistics
    last_extract = DateTimeField()
    last_successful_extract = DateTimeField()
    extract_error = StringField()
    last_load = DateTimeField()
    last_successful_load = DateTimeField()
    last_extract_event = DateTimeField()
    load_error = StringField()
    # Object id in BI
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _name_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        return self.name

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, oid: Union[str, bson.ObjectId]) -> Optional["RemoteSystem"]:
        return RemoteSystem.objects.filter(id=oid).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_name_cache"), lock=lambda _: id_lock)
    def get_by_name(cls, name: str) -> Optional["RemoteSystem"]:
        return RemoteSystem.objects.filter(name=name).first()

    @property
    def config(self):
        if not hasattr(self, "_config"):
            self._config = {e.key: e.value for e in self.environment}
        return self._config

    @property
    def managed_object_as_discovered(self) -> bool:
        return self.managed_object_loader_policy == "D"

    def get_handler(self):
        """
        Return BaseTTSystem instance
        """
        h = get_handler(str(self.handler))
        if not h:
            raise ValueError
        return h(self)

    def get_extractors(self):
        extractors = []
        for k in self._fields:
            if k.startswith("enable_") and getattr(self, k):
                extractors += [k[7:]]
        return extractors

    def extract(self, extractors=None, quiet=False, incremental=False, checkpoint=None):
        extractors = extractors or self.get_extractors()
        error = None
        try:
            self.get_handler().extract(extractors, incremental=incremental, checkpoint=checkpoint)
        except Exception as e:
            if not quiet:
                raise e
            error_report()
            error = str(e)
        self.last_extract = datetime.datetime.now()
        if not error:
            self.last_successful_extract = self.last_extract
        self.extract_error = error
        self.save()

    def load(self, extractors=None, quiet=False):
        extractors = extractors or self.get_extractors()
        error = None
        try:
            self.get_handler().load(extractors)
        except Exception as e:
            if not quiet:
                raise e
            error_report()
            error = str(e)
        self.last_load = datetime.datetime.now()
        if not error:
            self.last_successful_load = self.last_load
        self.load_error = error
        self.save()

    def check(self, extractors=None):
        extractors = extractors or self.get_extractors()
        try:
            return self.get_handler().check(extractors)
        except Exception:
            error_report()

    def get_loader_chain(self):
        return self.get_handler().get_loader_chain()
