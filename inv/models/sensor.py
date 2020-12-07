# ----------------------------------------------------------------------
# Sensor model
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from threading import Lock
import operator
from typing import Dict

# Third-party modules
from mongoengine.document import Document
from mongoengine.fields import StringField, IntField, LongField
import cachetools

# NOC modules
from noc.wf.models.state import State
from noc.core.wf.decorator import workflow
from noc.core.bi.decorator import bi_sync
from noc.core.mongo.fields import PlainReferenceField, ForeignKeyField
from noc.inv.models.object import Object
from noc.sa.models.managedobject import ManagedObject
from noc.pm.models.measurementunits import MeasurementUnits
from .sensorprofile import SensorProfile


id_lock = Lock()
logger = logging.getLogger(__name__)


@bi_sync
@workflow
class Sensor(Document):
    meta = {"collection": "sensors", "strict": False, "auto_create_index": False}

    profile = PlainReferenceField(SensorProfile, default=SensorProfile.get_default_profile)
    object = PlainReferenceField(Object)
    managed_object = ForeignKeyField(ManagedObject)
    local_id = StringField()
    state = PlainReferenceField(State)
    units = PlainReferenceField(MeasurementUnits)
    label = StringField()
    dashboard_label = StringField()
    protocol = StringField(choices=["modbus_rtu", "modbus_ascii", "modbus_tcp", "snmp", "ipmi"])
    modbus_register = IntField()
    snmp_oid = StringField()
    bi_id = LongField(unique=True)

    _id_cache = cachetools.TTLCache(maxsize=100, ttl=60)
    _bi_id_cache = cachetools.TTLCache(maxsize=100, ttl=60)

    def __str__(self):
        if self.object:
            return "%s: %s" % (self.object, self.local_id)
        return "%s: %s" % (self.units, self.local_id)

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_id_cache"), lock=lambda _: id_lock)
    def get_by_id(cls, id):
        return Sensor.objects.filter(id=id).first()

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_bi_id_cache"), lock=lambda _: id_lock)
    def get_by_bi_id(cls, id):
        return Sensor.objects.filter(bi_id=id).first()

    @classmethod
    def sync_object(cls, obj: Object) -> None:
        """
        Synchronize sensors with object model
        :param obj:
        :return:
        """
        # Get existing sensors
        obj_sensors: Dict[str, Sensor] = {s.name: s for s in Sensor.objects.filter(object=obj.id)}
        m_proto = [
            d.value
            for d in obj.get_effective_data()
            if d.interface == "modbus" and d.attr == "type"
        ] or ["rtu"]
        # Create new sensors
        for sensor in obj.model.sensors:
            if sensor.name in obj_sensors:
                del obj_sensors[sensor.name]
                continue
            #
            logger.info(
                "[%s|%s] Creating new sensor '%s'", obj.name if obj else "-", "-", sensor.name
            )
            s = Sensor(
                profile=SensorProfile.get_default_profile(),
                object=obj,
                local_id=sensor.name,
                units=sensor.units,
            )
            # Get sensor protocol
            if sensor.modbus_register:
                if not m_proto:
                    continue
                s.protocol = "modbus_%s" % m_proto[0].lower()
                s.modbus_register = sensor.modbus_register
            elif sensor.snmp_oid:
                s.protocol = "snmp"
                s.snmp_oid = sensor.snmp_oid
            else:
                logger.info(
                    "[%s|%s] Unknown sensor protocol '%s'",
                    obj.name if obj else "-",
                    "-",
                    sensor.name,
                )
            s.save()
        # Notify missed sensors
        for s in sorted(obj_sensors):
            sensor = obj_sensors[s]
            logger.info("[%s|%s] Sensor is missed '%s'", obj.name if obj else "-", "-", sensor.name)
            sensor.fire_event("missed")
