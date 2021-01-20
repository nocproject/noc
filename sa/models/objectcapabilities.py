# ----------------------------------------------------------------------
# Object Capabilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import ListField, EmbeddedDocumentField

# NOC modules
from noc.inv.models.capability import Capability
from .managedobject import ManagedObject, CREDENTIAL_CACHE_VERSION
from noc.core.mongo.fields import ForeignKeyField
from noc.core.model.decorator import on_save
from noc.core.cache.base import cache
from noc.core.datastream.decorator import datastream
from noc.inv.models.capsitem import CapsItem

logger = logging.getLogger(__name__)


@on_save
@datastream
class ObjectCapabilities(Document):
    meta = {"collection": "noc.sa.objectcapabilities", "strict": False, "auto_create_index": False}
    object = ForeignKeyField(ManagedObject, primary_key=True)
    caps = ListField(EmbeddedDocumentField(CapsItem))

    def __str__(self):
        return "%s caps" % self.object.name

    def on_save(self):
        cache.delete("cred-%s" % self.object.id, version=CREDENTIAL_CACHE_VERSION)

    def iter_changed_datastream(self, changed_fields=None):
        yield "managedobject", self.object.id

    @classmethod
    def get_capabilities(cls, object):
        """
        Resolve object capabilities
        :param object: ManagedObject instance or id
        :return: dict of capability name -> current value
        """
        if hasattr(object, "id"):
            object = object.id
        caps = {}
        oc = ObjectCapabilities._get_collection().find_one({"_id": object})
        if oc:
            for c in oc["caps"]:
                cc = Capability.get_by_id(c["capability"])
                if cc:
                    caps[cc.name] = c.get("value")
        return caps

    @classmethod
    def update_capabilities(cls, object, caps, source):
        """
        Update stored capabilities
        :param object:
        :param caps:
        :param source:
        :return:
        """
        o_label = object
        if hasattr(object, "id"):
            o_label = object.name
            object = object.id
        o_label += "|%s" % source
        oc = ObjectCapabilities._get_collection().find_one({"_id": object}) or {}
        # Update existing capabilities
        new_caps = []
        seen = set()
        changed = False
        for ci in oc.get("caps", []):
            c = Capability.get_by_id(ci["capability"])
            cs = ci.get("source")
            cv = ci.get("value")
            if not c:
                logger.info("[%s] Removing unknown capability id %s", o_label, ci["capability"])
                continue
            cn = c.name
            seen.add(cn)
            if cs == source:
                if cn in caps:
                    if caps[cn] != cv:
                        logger.info(
                            "[%s] Changing capability %s: %s -> %s", o_label, cn, cv, caps[cn]
                        )
                        ci["value"] = caps[cn]
                        changed = True
                else:
                    logger.info("[%s] Removing capability %s", o_label, cn)
                    changed = True
                    continue
            elif cn in caps:
                logger.info(
                    "[%s] Not changing capability %s: " "Already set with source '%s'",
                    o_label,
                    cn,
                    cs,
                )
            new_caps += [ci]
        # Add new capabilities
        for cn in set(caps) - seen:
            c = Capability.get_by_name(cn)
            if not c:
                logger.info("[%s] Unknown capability %s, ignoring", o_label, cn)
                continue
            logger.info("[%s] Adding capability %s = %s", o_label, cn, caps[cn])
            new_caps += [{"capability": c.id, "value": caps[cn], "source": source}]
            changed = True

        if changed:
            logger.info("[%s] Saving changes", o_label)
            ObjectCapabilities._get_collection().update(
                {"_id": object}, {"$set": {"caps": new_caps}}, upsert=True
            )
            cache.delete("cred-%s" % object, version=CREDENTIAL_CACHE_VERSION)
        caps = {}
        for ci in new_caps:
            cn = Capability.get_by_id(ci["capability"])
            if cn:
                caps[cn.name] = ci.get("value")
        return caps
