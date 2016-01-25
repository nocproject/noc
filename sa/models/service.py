# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import logging
from collections import defaultdict
## Third-party modules
from mongoengine.document import Document, EmbeddedDocument
from mongoengine.fields import (StringField, DateTimeField, DictField,
                                ReferenceField, IntField,
                                EmbeddedDocumentField, ListField,
                                ObjectIdField)
## NOC modules
from serviceprofile import ServiceProfile
from noc.crm.models.supplier import Supplier
from noc.crm.models.subscriber import Subscriber
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.lib.nosql import ForeignKeyField
from noc.core.model.decorator import on_save, on_delete
from noc.models import get_object, get_model

logger = logging.getLogger(__name__)


class ServiceDependency(EmbeddedDocument):
    name = StringField()
    # Depended service
    service = ObjectIdField()
    # Root cause for critical status
    root = ObjectIdField()


@on_save
@on_delete
class Service(Document):
    meta = {
        "collection": "noc.services",
        "indexes": [
            "dependencies.service"
        ]
    }

    profile = ReferenceField(ServiceProfile, required=True)
    label = StringField()
    # Creation timestamp
    ts = DateTimeField(default=datetime.datetime.now)
    # Service data
    data = DictField()
    #
    supplier = ReferenceField(Supplier)
    subscriber = ReferenceField(Subscriber)
    #
    administrative_domain = ForeignKeyField(AdministrativeDomain)
    # Logical state of service
    logical_status = StringField(
            choices=[
                ("P", "Planned"),
                ("p", "Provisioning"),
                ("T", "Testing"),
                ("R", "Ready"),
                ("S", "Suspended"),
                ("r", "Removing"),
                ("C", "Closed")
            ],
            default="R"
    )
    # Effective status, calculated from both self and dependency status
    status = IntField()
    # Measured status
    self_status = IntField()
    # Calculated dependencies status
    depended_status = IntField()
    # Dependencies
    dependencies = ListField(EmbeddedDocumentField(ServiceDependency),
                     default=[])
    # direction, copied from type
    direction = StringField(
        choices=[
            ("C", "CFS"),
            ("R", "RFS")
        ],
        default="C"
    )

    # Service status constants
    SS_UNKNOWN = None
    SS_CRITICAL = 0
    SS_DEGRADED = 10
    SS_WARNING = 20
    SS_OK = 30

    class BindError(Exception):
        pass

    def __unicode__(self):
        return self.label or unicode(self.id)

    def on_save(self):
        pass

    def on_delete(self):
        pass

    @classmethod
    def create_service(cls):
        """
        Create new service
        """
        pass
    
    def get_effective_status(self):
        """
        Returns effected status from *self* and *depended_status*
        """
        ss = []
        if self.self_status is not None:
            ss += [self.self_status]
        if self.dependend_status is not None:
            ss += [self.dependend_status]
        return min(ss or [None])

    def get_depended_status(self):
        """
        Calculate depended status
        """
        ds = set(d.service for d in self.dependencies)
        dsn = defaultdict(list)
        for d in self.dependencies:
            dsn[d.name] += [d.service]
        # Get depended services status
        r = Service.objects.aggregate([
            {
                "$match": {
                    "_id": {
                        "$in": list(ds)
                    }
                }
            },
            {
                "$project": {
                    "status": True
                }
            }
        ])
        ss = dict((x["_id"], x["status"]) for x in r["result"])
        # Check each dependency group
        dgs = {}
        for dg in self.profile.dependencies:
            if not dg.propagate_status:
                continue
            # Get all services statuses for group
            states = [ss.get(sn) for sn in dsn[dg.name]]
            # Skip unknown states and sort
            states = sorted(ss for ss in states if ss is not None)
            # Skip most faulty states when possible
            if dg.min_ok and len(states) > dg.min_ok:
                dgs[dg.name] = states[dg.min_ok:]
            dgs[dg.name] = states[0] if states else None
        # Get worst status
        ss = sorted(s for s in dgs.itervalues() if s is not None)
        return ss[0] if ss else None

    def set_status(self, status):
        """
        Update *self_status* and propagate faults when necessary
        """
        logger.debug("[%s] Measured status changed: %s -> %s",
                     self.id, self.self_status, status)
        # Store self status
        self.self_status = status
        # Calculate effective status
        new_status = self.get_effective_status()
        if new_status == self.status:
            return
        logger.debug("[%s] Effective status changed: %s -> %s",
                     self.id, self.status, new_status)
        self.status = new_status
        self.save()
        self.propagate_status()

    def propagate_status(self, root=None):
        """
        Propagate status changes to all dependencies
        """
        root = root or self
        for svc in Service.objects.filter(deps__service=self.id):
            ds = svc.get_depended_status()
            if ds == svc.depended_status:
                continue  # Not changed
            logger.debug("[%s] Depended status changed: %s -> %s",
                         svc.id, svc.depended_status, ds)
            svc.depended_status = ds
            es = svc.get_effective_status()
            status_change = es != self.status
            if status_change:
                logger.debug("[%s] Effective status changed: %s -> %s",
                             svc.id, svc.status, es)
                self.status = es
            svc.save()
            if status_change:
                svc.propagate_status(root)

    @property
    def object(self):
        """
        Referenced object
        """
        if not self.object:
            return None
        else:
            return get_object(self.model, self.object)

    def bind(self, object):
        """
        Bind object to service
        """
        nb = self.bound_objects.count()
        if nb >= self.profile.bind_limit:
            logger.debug(
                    "Cannot bind object %s to service %s. Bind limit exceeded",
                    object, self.id
            )
            raise self.BindError()
        logger.debug("Bind object %s to service %s", object, self.id)
        object.service = self
        object.save()

    @property
    def bound_objects(self):
        """
        Queryset returning all unbound object
        """
        model = get_model(self.profile.type.model)
        return model.objects.filter(service=self)

    def unbind(self, object):
        """
        Unbind service from all objects
        """
        logger.debug("Unbind object %s from service %s", object, self.id)
        object.service = None
        object.save()
