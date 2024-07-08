# ----------------------------------------------------------------------
# Service Instance
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, Union

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    BooleanField,
    IntField,
    DateTimeField,
    FloatField,
    ObjectIdField,
    ListField,
)

# NOC modules
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.sa.models.managedobject import ManagedObject

SOURCES = {"discovery", "etl", "manual"}


class ServiceInstance(Document):
    """
    Service Instance.

    Service Instance. Binding Service to
    resource and os process


    Attributes:
        service: Reference to Service
        resource: Resource Id
    """

    meta = {
        "collection": "serviceinstances",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["service", "managed_object", ("address", "port")],
    }
    name: str = StringField(required=True)
    service = PlainReferenceField("sa.Service", required=True)
    # For port services
    managed_object = ForeignKeyField(ManagedObject, required=False)
    interface_id = ObjectIdField()  # Interface mapping
    # subinterface_id = ObjectIdField()  # Subinterface mapping cache
    address = StringField()
    fqdn = StringField()
    # ? discriminator
    # Sources that find sensor
    sources = ListField(StringField(choices=list(SOURCES)))
    port = IntField(min_value=0, max_value=65536)
    # NRI port id, converted by portmapper to native name
    nri_port = StringField()
    # Object id in remote system
    remote_id = StringField()
    # CPE
    resource = StringField(required=False)
    status: bool = BooleanField()
    # Timestamp of last confirmation
    last_seen = DateTimeField()
    uptime = FloatField(default=0)
    # used by
    # labels ?

    def __str__(self) -> str:
        name = self.name or self.service.label
        if self.managed_object:
            return f"{self.managed_object.name} - {name}"
        if self.address:
            return f"{self.address}:{self.port} - {name}"
        return name

    def on_save(self):
        if not hasattr(self, "_changed_fields") or "nri_port" in self._changed_fields:
            pass
        #    self.unbind_interface()

    @property
    def interface(self):
        from noc.inv.models.interface import Interface
        from noc.inv.models.subinterface import SubInterface

        if self.subinterface_id:
            return SubInterface.objects.filter(id=self.subinterface).first()
        if self.interface_id:
            return Interface.objects.filter(id=self.interface_id).first()
        return None

    def seen(
        self,
        source: Optional[str] = None,
        address: Optional[str] = None,
        port: Optional[str] = None,
        ts: Optional[datetime.datetime] = None,
    ):
        """
        Seen Instance
        """
        if source and source in SOURCES:
            self.sources = list(set(self.sources or []).union({source}))
            self._get_collection().update_one({"_id": self.id}, {"$addToSet": {"sources": source}})
        elif source and source not in SOURCES:
            self.sources.append(source)
            self._get_collection().update_one({"_id": self.id}, {"$addToSet": {"sources": source}})

    def unseen(self, source: Optional[str] = None):
        """
        Unseen Instance on current source
        """
        if source and source in SOURCES:
            self.sources = list(set(self.sources or []) - {source})
            self._get_collection().update_one({"_id": self.id}, {"$pull": {"sources": source}})
        elif not source:
            # For empty source, clean sources
            self.sources = []
            self._get_collection().update_one({"_id": self.id}, {"$set": {"sources": []}})
            # delete
