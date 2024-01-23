# ---------------------------------------------------------------------
# Link model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import datetime
from typing import Optional, Union

# Third-party modules
from bson import ObjectId
from mongoengine.document import Document
from mongoengine.fields import StringField, DateTimeField, ListField, IntField, ObjectIdField

# NOC modules
from noc.config import config
from noc.core.mongo.fields import PlainReferenceListField
from noc.core.model.decorator import on_delete, on_save
from noc.core.change.decorator import change
from noc.core.comp import smart_text
from noc.main.models.label import Label


@on_delete
@on_save
@change
class Link(Document):
    """
    Network links.
    Always contains a list of 2*N references.
    2 - for fully resolved links
    2*N for unresolved N-link portchannel
    N, N > 2 - broadcast media
    """

    meta = {
        "collection": "noc.links",
        "strict": False,
        "auto_create_index": False,
        "indexes": ["interfaces", "linked_objects", "linked_segments"],
    }

    # Optional link name
    name = StringField()
    # Optional description
    description = StringField()
    # Optional shape
    shape = StringField()
    # List of interfaces
    interfaces = PlainReferenceListField("inv.Interface")
    # Link type, detected automatically
    type = StringField(
        choices=[
            # 2 managed objects, 2 linked interfaces
            ("p", "Point-to-Point"),
            # 2 managed objects, even number of linked interfaces (>2)
            ("a", "Point-to-Point Aggregated"),
            # >2 managed objects, one uplink
            ("m", "Point-to-Multipoint"),
            # >2 managed objects, no dedicated uplink
            ("M", "Multipoint-to-Multipoint"),
            # Unknown
            ("u", "Unknown"),
        ],
        default="u",
    )
    # List of linked objects
    linked_objects = ListField(IntField())
    # List of linked segments
    linked_segments = ListField(ObjectIdField())
    # Name of discovery method or "manual"
    discovery_method = StringField()
    # Timestamp of first discovery
    first_discovered = DateTimeField(default=datetime.datetime.now)
    # Timestamp of last confirmation
    last_seen = DateTimeField()
    # L2 path cost
    l2_cost = IntField(default=1)
    # L3 path cost
    l3_cost = IntField(default=1)

    def __str__(self):
        if self.interfaces:
            return "(%s)" % ", ".join(smart_text(i) for i in self.interfaces)
        else:
            return "Stale link (%s)" % self.id

    @classmethod
    def get_by_id(cls, oid: Union[str, ObjectId]) -> Optional["Link"]:
        return Link.objects.filter(id=oid).first()

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_managedobject:
            for mo_id in self.linked_objects:
                yield "managedobject", mo_id

    def clean(self):
        self.linked_objects = list(sorted(set(i.managed_object.id for i in self.interfaces)))
        self.linked_segments = list(
            sorted(set(i.managed_object.segment.id for i in self.interfaces))
        )
        self.type = self.get_type()

    def contains(self, iface):
        """
        Check link contains interface
        :return: boolean
        """
        return iface in self.interfaces

    @property
    def is_ptp(self) -> bool:
        """
        Check link is point-to-point link
        :return:
        """
        return self.type == "p" or self.type == "a"

    @property
    def is_lag(self) -> bool:
        """
        Check link is unresolved LAG
        :return:
        """
        return self.type == "p" or self.type == "a"

    @property
    def is_broadcast(self) -> bool:
        """
        Check link is broadcast media
        :return:
        """
        return not self.is_ptp and not self.is_lag

    @property
    def is_loop(self) -> bool:
        """
        Check link is looping to same object
        :return:
        """
        return len(self.linked_objects) == 1

    @property
    def interface_ids(self):
        """
        Returns list of interface ids, avoiding dereference
        :return:
        """

        def q(i):
            if hasattr(i, "id"):
                return i.id
            return i

        return [q(iface) for iface in self._data.get("interfaces", [])]

    def other(self, interface):
        """
        Return other interfaces of the link
        :param interface:
        :return:
        """
        return [i for i in self.interfaces if i.id != interface.id]

    def other_ptp(self, interface):
        """
        Return other interface of ptp link
        :param interface:
        :return:
        """
        return self.other(interface)[0]

    def touch(self, method=None):
        """
        Touch last_seen
        """
        now = datetime.datetime.now()
        op = {"last_seen": now}
        self.last_seen = now
        if method:
            self.discovery_method = method
            op["discovery_method"] = method
        # Do not save to prevent rebuilding topology
        self._get_collection().update_one({"_id": self.id}, {"$set": op})
        # self.save()

    @classmethod
    def object_links(cls, object):
        return Link.objects.filter(linked_objects=object.id)

    @classmethod
    def object_links_count(cls, object):
        return Link.objects.filter(linked_objects=object.id).count()

    def on_save(self):
        from noc.sa.models.managedobject import ManagedObject

        if not hasattr(self, "_changed_fields") or "interfaces" in self._changed_fields:
            self.update_topology()
            Label.add_model_labels(
                "inv.Interface",
                ["noc::is_linked::="],
                instance_filters=[("_id", [i.id for i in self.interfaces])],
            )
            ManagedObject.update_links(self.linked_objects)

    def on_delete(self):
        from noc.sa.models.managedobject import ManagedObject

        self.update_topology()
        # Assumption that Interface has only one Link :)
        Label.remove_model_labels(
            "inv.Interface",
            ["noc::is_linked::="],
            instance_filters=[("_id", [i.id for i in self.interfaces])],
        )
        ManagedObject.update_links(self.linked_objects, exclude_link_ids=[self.id])

    @property
    def managed_objects(self):
        """
        List of connected managed objects
        """
        from noc.sa.models.managedobject import ManagedObject

        return list(ManagedObject.objects.filter(id__in=list(self.linked_objects)))

    @property
    def segments(self):
        """
        List of segments connected by link
        :return:
        """
        from noc.inv.models.networksegment import NetworkSegment

        return list(NetworkSegment.objects.filter(id__in=self.linked_segments))

    def update_topology(self):
        for mo in self.managed_objects:
            mo.update_topology()

    def get_type(self):
        """
        Detect link type
        :return: Link type as value for .type
        """
        n_objects = len(self.linked_objects)
        n_interfaces = len(self.interfaces)
        if n_objects == 2 and n_interfaces == 2:
            return "p"  # Point-to-point
        if n_objects == 2 and n_interfaces > 2 and n_interfaces % 2 == 0:
            d = defaultdict(int)  # object -> count
            for i in self.interfaces:
                d[i.managed_object.id] += 1
            k = list(d)
            if d[k[0]] == d[k[1]]:
                return "a"  # Point-to-Point aggregated
        if n_objects > 2:
            if self.type == "m":
                return "m"
            else:
                return "M"
        return "u"

    def reset_label(self):
        coll = Link._get_collection()
        # Check ManagedObject Link Count
        r = [
            c["_id"]
            for c in coll.aggregate(
                [
                    {"$match": {"linked_objects": {"$in": self.linked_objects}}},
                    {"$unwind": "$linked_objects"},
                    {"$group": {"_id": "$linked_objects", "count": {"$sum": 1}}},
                    {"$match": {"count": {"$gt": 1}, "_id": {"$in": self.linked_objects}}},
                ]
            )
        ]
        # Not Reset device more that 1 link
        rl = set(self.linked_objects) - set(r)
        if rl:
            Label.remove_model_labels(
                "sa.ManagedObject", ["noc::is_linked::="], instance_filters=[("id", list(rl))]
            )
        # Assumption that Interface has only one Link :)
        Label.remove_model_labels(
            "inv.Interface",
            ["noc::is_linked::="],
            instance_filters=[("_id", [i.id for i in self.interfaces])],
        )
