# ---------------------------------------------------------------------
# Asset check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict
import hashlib
import base64
from threading import Lock
import operator
import re
from typing import Optional, List, Dict, Set, Tuple, Iterable, Any, Union

# Third-party modules
import cachetools

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.main.models.label import Label
from noc.inv.models.modelinterface import ModelInterface, ModelDataError
from noc.inv.models.objectmodel import ObjectModel, ConnectionRule, Crossing
from noc.inv.models.object import Object, ObjectAttr
from noc.inv.models.vendor import Vendor
from noc.inv.models.unknownmodel import UnknownModel
from noc.inv.models.modelmapping import ModelMapping
from noc.inv.models.error import ConnectionError
from noc.inv.models.sensor import Sensor
from noc.inv.models.sensorprofile import SensorProfile
from noc.inv.models.cpe import CPE
from noc.pm.models.measurementunits import MeasurementUnits, DEFAULT_UNITS_NAME
from noc.core.text import str_dict
from noc.core.comp import smart_bytes


class AssetCheck(DiscoveryCheck):
    """
    Version discovery
    """

    name = "asset"
    required_script = "get_inventory"

    _serial_masks = {}
    _serial_masks_lock = Lock()
    _builtin_interfaces = {"asset", "stack", "management"}

    fatal_errors = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unknown_part_no: Dict[str, Set[str]] = {}  # part_no -> list of variants
        self.pn_description: Dict[str, str] = {}  # part_no -> Description
        self.vendors: Dict[str, Vendor] = {}  # code -> Vendor instance
        self.objects: List[
            Tuple[
                str,
                Union[Object, str],
                Dict[str, Union[int, str]],
                Optional[str],
                List[ObjectAttr],
                List[ObjectAttr],
            ]
        ] = []  # [(type, object, context, serial, data)]
        self.sensors: Dict[Tuple[Optional[Object], str] : Dict[str, Any]] = (
            {}
        )  # object, sensor -> sensor data
        # Upper object, lower object
        self.to_disconnect: Set[Tuple[Object, Object]] = set()
        self.rule: Dict[str, List[ConnectionRule]] = defaultdict(
            list
        )  # Connection rule. type -> [rule1, ruleN]
        self.rule_context = {}
        self.ctx: Dict[str, Union[int, str]] = {}
        self.stack_member: Dict["Object", str] = {}  # object -> stack member numbers
        self.managed: Set[str] = set()  # Object ids
        self.unk_model: Dict[str, ObjectModel] = {}  # name -> model
        self.lost_and_found = self.get_lost_and_found(self.object)
        self.generic_vendor = Vendor.get_by_code("GENERIC")
        self.noname_vendor = Vendor.get_by_code("NONAME")
        self.generic_models: List[str] = self.get_generic_models()
        # CPEs
        self.cpes: Dict[str, Tuple[str, str, str, str, str]] = self.load_cpe()
        #
        self.object_param_artifacts: Dict[str, List[Dict[str, Any]]] = {}  # oid: [Data]

    def handler(self):
        self.logger.info("Checking assets")
        result = self.object.scripts.get_inventory()
        self.find_managed()
        # Submit objects
        for o in result:
            self.logger.info("Submit %s", str_dict(o))
            # Split data to Constant and ObjectData
            self.submit(
                o_type=o["type"],
                number=o.get("number"),
                builtin=o["builtin"],
                vendor=o.get("vendor"),
                part_no=o["part_no"],
                revision=o.get("revision"),
                serial=o.get("serial"),
                mfg_date=o.get("mfg_date"),
                description=o.get("description"),
                sensors=o.get("sensors"),
                sa_data=o.get("data"),
                param_data=o.get("param_data"),
                crossing=o.get("crossing"),
            )
            # cpe_objects
        # Assign stack members
        self.submit_stack_members()
        #
        self.submit_connections()
        #
        self.check_management()
        #
        self.disconnect_connections()
        #
        self.sync_sensors()
        #
        self.logger.info("CPE Processed: %s", len(self.cpes))
        for cpe_id, (_, _, vendor, model, sn) in self.cpes.items():
            self.submit(
                o_type="CHASSIS",
                number="0",
                vendor=vendor,
                part_no=[model],
                serial=sn,
                cpe_id=cpe_id,
            )
        #
        self.set_artefact("object_param_artifacts", self.object_param_artifacts)

    def submit(
        self,
        o_type: str,
        part_no: List[str],
        number: Optional[str] = None,
        builtin: bool = False,
        vendor: Optional[str] = None,
        revision: Optional[str] = None,
        serial: Optional[str] = None,
        mfg_date: Optional[str] = None,
        description: Optional[str] = None,
        sensors: List[Dict[str, Any]] = None,
        sa_data: List[Dict[str, Any]] = None,
        param_data: List[Dict[str, Any]] = None,
        cpe_id: Optional[str] = None,
        crossing: List[Dict[str, str]] | None = None,
    ):
        # Check the vendor and the serial are sane
        # OEM transceivers return binary trash often
        if vendor:
            # Possible dead code
            try:
                vendor.encode("utf-8")
            except UnicodeDecodeError:
                self.logger.info("Trash submitted as vendor id: %s", vendor.encode("hex"))
                return
        if serial:
            # Possible dead code
            try:
                serial.encode("utf-8")
            except UnicodeDecodeError:
                self.logger.info("Trash submitted as serial: %s", serial.encode("hex"))
                return
        #
        data, constant_data = self.clean_sa_data(sa_data)
        is_unknown_xcvr = not builtin and part_no[0].startswith("Unknown | Transceiver | ")
        if not o_type and is_unknown_xcvr:
            o_type = "XCVR"
        # Skip builtin modules
        if builtin:
            # Adjust context anyway
            self.prepare_context(o_type, number)
            return  # Builtin must aways have type set
        #
        if is_unknown_xcvr:
            self.logger.info("%s S/N %s should be resolved later", part_no[0], serial)
            self.prepare_context(o_type, number)
            self.objects += [("XCVR", part_no[0], self.ctx.copy(), serial, data, constant_data)]
            return
        # Cache description
        if description:
            for p in part_no:
                if p not in self.pn_description:
                    self.pn_description[p] = description
        # Find vendor
        vnd = self.get_vendor(vendor, o_type)
        if not vnd:
            # Try to resolve via model map
            m = self.get_model_map(vendor, part_no, serial, cpe_id)
            if not m:
                self.logger.error(
                    "Unknown vendor '%s' for S/N %s (%s)", vendor, serial, description
                )
                return
        else:
            # Find model
            m = ObjectModel.get_model(vnd, part_no)
            if not m:
                # Try to resolve via model map
                m = self.get_model_map(vendor, part_no, serial, cpe_id)
                if not m:
                    if o_type == "XCVR":
                        self.logger.info(
                            "Unknown model: vendor=%s, part_no=%s (%s). Try resolve later",
                            vnd.name,
                            part_no,
                            description,
                        )

                        self.prepare_context(o_type, number)
                        self.objects += [
                            ("XCVR", part_no[0], self.ctx.copy(), serial, data, constant_data)
                        ]
                        return
                    else:
                        self.logger.info(
                            "Unknown model: vendor=%s, part_no=%s (%s). Skipping...",
                            vnd.name,
                            part_no,
                            description,
                        )
                        self.register_unknown_part_no(vnd, part_no, description)
                        return

        # Sanitize serial number against the model
        serial = self.clean_serial(m, number, serial)
        #
        if m.cr_context and o_type != m.cr_context:
            # Override type with object mode's one
            self.logger.info("Model changes type to '%s'", m.cr_context)
            o_type = m.cr_context
        if not o_type:
            self.logger.info(
                "Cannot resolve type for: vendor=%s, part_no=%s (%s). Skipping...",
                vnd.name,
                description,
                part_no,
            )
            return
        self.prepare_context(o_type, number)
        # Get connection rule
        if not self.rule and m.connection_rule:
            self.set_rule(m.connection_rule)
            # Set initial context
            if o_type in self.rule_context:
                scope = self.rule_context[o_type][0]
                if scope:
                    self.set_context(scope, number)
        # Find existing object or create new
        o: Optional["Object"] = Object.objects.filter(
            model__in=[m.id] + self.generic_models,
            data__match={"interface": "asset", "attr": "serial", "value": serial},
        ).first()
        if not o:
            # Create new object
            self.logger.info("Creating new object. model='%s', serial='%s'", m.name, serial)
            o_data = [
                ObjectAttr(scope="", interface="asset", attr="part_no", value=[part_no]),
                ObjectAttr(scope="", interface="asset", attr="serial", value=serial),
            ]
            if revision:
                o_data += [ObjectAttr(scope="", interface="asset", attr="revision", value=revision)]
            if mfg_date:
                o_data += [ObjectAttr(scope="", interface="asset", attr="mfg_date", value=mfg_date)]
            o = Object(
                model=m,
                data=o_data,
                parent=self.object.container if self.object.container else self.lost_and_found,
            )
            o.save()
            o.log(
                "Created by asset_discovery",
                system="DISCOVERY",
                managed_object=self.object,
                op="CREATE",
            )
        elif o.is_generic:
            """
            Generic Template
            """
            o.model = m
            o.log(
                f"Object Model changed: Generic -> {m.name}",
                system="DISCOVERY",
                managed_object=self.object,
                op="CHANGE",
            )
        else:
            # Add all inner connection to disconnect list
            self.to_disconnect.update((o, c) for c in o.iter_children())
        # Check revision
        if o.get_data("asset", "revision") != revision:
            # Update revision
            self.logger.info(
                "Object revision changed [%s %s] %s -> %s",
                m.name,
                o.id,
                o.get_data("asset", "revision"),
                revision,
            )
            o.set_data("asset", "revision", revision)
            o.save()
            o.log(
                "Object revision changed: %s -> %s" % (o.get_data("asset", "revision"), revision),
                system="DISCOVERY",
                managed_object=self.object,
                op="CHANGE",
            )
        # Check manufacturing date
        if mfg_date and o.get_data("asset", "revision") != revision:
            # Update revision
            self.logger.info(
                "Object manufacturing date changed [%s %s] %s -> %s",
                m.name,
                o.id,
                o.get_data("asset", "mfg_date"),
                mfg_date,
            )
            o.set_data("asset", "mfg_date", mfg_date)
            o.save()
            o.log(
                "Object manufacturing date: %s -> %s" % (o.get_data("asset", "mfg_date"), mfg_date),
                system="DISCOVERY",
                managed_object=self.object,
                op="CHANGE",
            )
        # Check management
        if o.get_data("management", "managed") and not cpe_id:
            if o.get_data("management", "managed_object") != self.object.id:
                self.logger.info("Changing object management to '%s'", self.object.name)
                o.set_data("management", "managed_object", self.object.id)
                o.save()
                o.log(
                    "Management granted",
                    system="DISCOVERY",
                    managed_object=self.object,
                    op="CHANGE",
                )
            self.update_name(o)
            if o.id in self.managed:
                self.managed.remove(o.id)
        # Check CPE
        if o.get_data("cpe", "cpe"):
            if o.get_data("cpe", "cpe_id") != cpe_id:
                self.logger.info("Changing object CPE to '%s'", cpe_id)  # Global_id
                o.set_data("cpe", "cpe_id", cpe_id)
                o.save()
                o.log(
                    "CPE granted",
                    system="DISCOVERY",
                    managed_object=self.object,
                    op="CHANGE",
                )
            self.update_name(o, cpe_id)
        self.objects += [(o_type, o, self.ctx.copy(), serial, data, constant_data)]
        # Collect sensors
        if sensors:
            for s in sensors:
                self.sensors[(o, s["name"])] = s
        # Collect stack members
        if number and o.get_data("stack", "stackable"):
            self.stack_member[o] = number
        self.sync_data(o, data)
        if param_data:
            self.object_param_artifacts[str(o.id)] = param_data
        self.sync_crossing(o, crossing)

    def clean_sa_data(
        self, data: List[Dict[str, str]]
    ) -> Tuple[List[ObjectAttr], List[ObjectAttr]]:
        """
        Cleanup data from script, Split it to Object Data and Constant Data
        """
        o_data, c_data = [], []
        if not data:
            return [], []
        for d in data:
            interface, attr = d["interface"], d["attr"]
            try:
                attr = ModelInterface.get_interface_attr(interface, attr)
            except ModelDataError as e:
                self.logger.error("[%s|%s] Error on data: %s", interface, attr, e)
                continue
            try:
                value = attr._clean(d["value"])
            except ValueError:
                self.logger.warning(
                    "[%s|%s] Error when convert value: %s", interface, attr, d["value"]
                )
                continue
            if attr.is_const:
                c_data += [
                    ObjectAttr(scope="discovery", interface=interface, attr=attr.name, value=value)
                ]
            else:
                o_data += [
                    ObjectAttr(scope="discovery", interface=interface, attr=attr.name, value=value)
                ]
        return o_data, c_data

    def sync_data(self, obj: Object, data: List[ObjectAttr]):
        """
        Sync script data with object
        """
        o_data = {}
        changed = False
        for d in obj.data:
            if d.interface in self._builtin_interfaces or d.scope != "discovery":
                continue
            attr = ModelInterface.get_interface_attr(d.interface, d.attr)
            if attr.is_const:
                continue
            o_data[d.interface, d.attr] = d.value
        # Create and Update
        for d in data:
            value = o_data.pop((d.interface, d.attr), None)
            if value and value == d.value:
                # Same value
                continue
            obj.set_data(d.interface, d.attr, d.value, "discovery")
            obj.log(
                f"Object data {d.interface}|{d.attr} changed: {value} -> {d.value}",
                system="DISCOVERY",
                managed_object=self.object,
                op="CHANGE",
            )
            changed = True
        for interface, attr in o_data:
            obj.reset_data(interface, attr, scope="discovery")
            obj.log(
                f"Object data {interface}|{attr} reset",
                system="DISCOVERY",
                managed_object=self.object,
                op="CHANGE",
            )
            changed = True
        # Reset data
        if changed:
            obj.save()

    def prepare_context(self, o_type: str, number: Optional[str]):
        self.set_context("N", number)
        if o_type and o_type in self.rule_context:
            scope, reset_scopes = self.rule_context[o_type]
            if scope:
                self.set_context(scope, number)
            if reset_scopes:
                self.reset_context(reset_scopes)

    def update_name(self, obj: Object, cpe_id: Optional[str] = None):
        cpe = None
        if cpe_id:
            cpe = self.cpes[cpe_id][0]
        n = self.get_name(obj, self.object, cpe)
        if n and n != obj.name:
            obj.name = n
            self.logger.info("Changing name to '%s'", n)
            obj.save()
            obj.log(
                "Change name to '%s'" % n,
                system="DISCOVERY",
                managed_object=self.object,
                op="CHANGE",
            )

    def iter_object(
        self, i: int, scope: str, value: int, target_type: str, fwd: bool
    ) -> Iterable[Tuple[str, Union[Object, str], Dict[str, Union[int, str]]]]:
        # Search backwards
        if not fwd:
            for j in range(i - 1, -1, -1):
                o_type, obj, ctx, _, _, _ = self.objects[j]
                if scope in ctx and ctx[scope] == value:
                    if target_type == o_type:
                        yield o_type, obj, ctx
                else:
                    break
        # Search forward
        if fwd:
            for j in range(i + 1, len(self.objects)):
                o_type, obj, ctx, _, _, _ = self.objects[j]
                if scope in ctx and ctx[scope] == value:
                    if target_type == o_type:
                        yield o_type, obj, ctx
                else:
                    return

    def expand_context(self, s: str, ctx: Dict[str, int]) -> str:
        """
        Replace values in context
        """
        s = s or ""
        for c in ctx:
            s = s.replace("{%s}" % c, str(ctx[c]))
        return s

    def submit_connections(self):
        # Check connection rule is set
        if not self.rule:
            return
        for i, o in enumerate(self.objects):
            type, object, context, serial, data, m_data = o
            self.logger.info("Trying to connect #%d. %s (%s)", i, type, str_dict(context))
            if type not in self.rule:
                continue
            # Find applicable rule
            for r in self.rule[type]:
                found = False
                t_n = self.expand_context(r.target_number, context)
                if r.scope.startswith("-"):
                    scope = r.scope[1:]
                    fwd = True
                else:
                    scope = r.scope
                    fwd = False
                for t_type, t_object, t_ctx in self.iter_object(
                    i, scope, context.get(scope), r.target_type, fwd=fwd
                ):
                    if isinstance(t_object, str):
                        continue
                    if not t_n or t_n == t_ctx["N"]:
                        # Check target object has proper connection
                        t_c = self.expand_context(r.target_connection, context)
                        if not t_object.has_connection(t_c):
                            self.logger.debug(
                                "[%s|%s|%s] Unknown connection %s",
                                t_object,
                                t_object.model,
                                scope,
                                t_c,
                            )
                            continue
                        # Check source object has proper connection
                        m_c = self.expand_context(r.match_connection, context)
                        if isinstance(object, str):
                            # Resolving unknown object
                            o = self.resolve_object(object, m_c, t_object, t_c, serial, m_data)
                            if not o:
                                continue
                            object = o
                            self.sync_data(object, data)
                        if not object.has_connection(m_c):
                            continue
                        # Connect
                        self.logger.info(
                            "Connecting %s %s:%s -> %s %s:%s",
                            type,
                            context["N"],
                            m_c,
                            t_type,
                            t_ctx["N"],
                            t_c,
                        )
                        if object.get_data("twinax", "twinax") and m_c == object.get_data(
                            "twinax", "alias"
                        ):
                            self.connect_twinax(object, m_c, t_object, t_c)
                        else:
                            self.connect_p2p(object, m_c, t_object, t_c)
                        found = True
                        break
                if found:
                    break

    def connect_p2p(self, o1: Object, c1: str, o2: Object, c2: str):
        """
        Create P2P connection o1:c1 - o2:c2
        """
        try:
            o1.connect_p2p(c1, o2, c2)
        except ConnectionError as e:
            self.logger.error("Conection error: %s", e)
            return
        if (
            o1.parent
            and o1.parent_connection
            and o1.parent.id == o2.id
            and (o2, o1) in self.to_disconnect
            and o1.parent_connection == c2
        ):
            self.to_disconnect.remove((o2, o1))
        elif (
            o2.parent
            and o2.parent_connection
            and o2.parent.id == o1.id
            and (o1, o2) in self.to_disconnect
            and o2.parent_connection == c1
        ):
            self.to_disconnect.remove((o1, o2))

    def connect_twinax(self, o1: Object, c1: str, o2: Object, c2: str):
        """
        Connect twinax object o1 and virtual connection c1 to o2:c2
        """
        free_connections = []
        # Resolve virtual name c1 to real connection
        r_names = [o1.get_data("twinax", "connection%d" % i) for i in range(1, 3)]
        # Check connection is already exists
        for n in r_names:
            cn, o, c = o1.get_p2p_connection(n)
            if not cn:
                free_connections += [n]
                continue
            if o.id == o2.id and c == c2:
                # Already connected
                return
        # Check twinax has free connection
        if not free_connections:
            self.logger.error("Twinax has no free connections")
            return
        # Connect first free to o2:c2
        c = free_connections[0]
        self.logger.info("Using twinax connection '%s' instead of '%s'", c, c1)
        self.connect_p2p(o1, c, o2, c2)

    def sync_sensors(self):
        obj_sensors: Dict[Tuple[Optional[Object], str], Sensor] = {
            (s.object, s.local_id): s
            for s in Sensor.objects.filter(object__in=[s[0] for s in self.sensors])
        }
        for obj, sn in obj_sensors:
            si = obj_sensors[(obj, sn)]
            # @todo rename sensors, need sensor_num for deduplicate
            sf = self.sensors.get((obj, sn))
            if sf:
                # Exist
                self.update_sensor(
                    si,
                    status=sf["status"],
                    units=sf["measurement"],
                    label=sf.get("description"),
                    snmp_oid=sf.get("snmp_oid"),
                    ipmi_id=sf.get("ipmi_id"),
                    labels=sf.get("labels"),
                )
                del self.sensors[(obj, sn)]
            else:
                # Missed sensors
                si.unseen(source="asset")
        # Create new sensors
        for obj, sn in self.sensors:
            si = self.sensors[(obj, sn)]
            self.submit_sensor(
                obj=obj,
                name=sn,
                status=si["status"],
                units=si["measurement"],
                label=si.get("description"),
                snmp_oid=si.get("snmp_oid"),
                ipmi_id=si.get("ipmi_id"),
                labels=si.get("labels"),
            )
        self.update_caps(
            {"DB | Sensors": Sensor.objects.filter(managed_object=self.object.id).count()},
            source="asset",
        )

    def submit_sensor(
        self,
        obj: Object,
        name: str,
        status: bool = True,
        units: Optional[str] = "Scalar",
        label: Optional[str] = None,
        snmp_oid: Optional[str] = None,
        ipmi_id: Optional[str] = None,
        labels: List[str] = None,
    ):
        self.logger.info("[%s|%s] Creating new sensor '%s'", obj.name if obj else "-", "-", name)
        s = Sensor(
            profile=SensorProfile.get_default_profile(),
            object=obj,
            managed_object=self.object,
            label=label,
            local_id=name,
            units=self.normalize_sensor_units(units),
        )
        # Get sensor protocol
        if snmp_oid:
            s.protocol = "snmp"
            s.snmp_oid = snmp_oid
        elif ipmi_id:
            s.protocol = "ipmi"
            s.ipmi_id = ipmi_id
        else:
            self.logger.info(
                "[%s|%s] Unknown sensor protocol '%s'",
                obj.name if obj else "-",
                "-",
                name,
            )
        if labels is not None:
            for ll in labels:
                Label.ensure_label(ll, ["inv.Sensor"])
            s.labels = [ll for ll in labels if Sensor.can_set_label(ll)]
            s.extra_labels = {"sa": s.labels}
        s.save()
        s.seen(source="asset")

    def update_sensor(
        self,
        sensor: Sensor,
        status: bool = True,
        units: Optional[str] = "Scalar",
        label: Optional[str] = None,
        snmp_oid: Optional[str] = None,
        ipmi_id: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ):
        sensor.seen(source="asset")
        if not status:
            sensor.fire_event("down")
        else:
            sensor.fire_event("up")
        units = self.normalize_sensor_units(units)
        if sensor.units != units:
            sensor.units = units
        if label and sensor.label != label:
            sensor.label = label
        # Get sensor protocol
        if snmp_oid and snmp_oid != sensor.snmp_oid:
            sensor.protocol = "snmp"
            sensor.snmp_oid = snmp_oid
        elif ipmi_id and sensor.ipmi_id != ipmi_id:
            sensor.protocol = "ipmi"
            sensor.ipmi_id = ipmi_id
        sa_labels = sensor.extra_labels.get("sa", [])
        labels = labels or []
        for ll in labels:
            if ll in sa_labels:
                continue
            self.logger.info("[%s] Ensure Sensor label: %s", sensor.id, ll)
            Label.ensure_label(ll, ["inv.Sensor"])
        if labels != sa_labels:
            remove_labels = set(sa_labels).difference(set(labels))
            if remove_labels:
                sensor.labels = [ll for ll in sensor.labels if ll not in remove_labels]
            sensor.extra_labels["sa"] = labels
        if sensor.managed_object != self.object:
            sensor.managed_object = self.object
        sensor.save()

    def normalize_sensor_units(self, units: str) -> MeasurementUnits:
        units = MeasurementUnits.get_by_name(units)
        if not units:
            units = MeasurementUnits.get_by_name(DEFAULT_UNITS_NAME)
        return units

    def submit_stack_members(self):
        if len(self.stack_member) < 2:
            return
        for o in self.stack_member:
            m = self.stack_member[o]
            if o.get_data("stack", "member") != m:
                self.logger.info("Setting stack member %s", m)
                o.set_data("stack", "member", m)
                o.save()
                o.log(
                    "Setting stack member %s" % m,
                    system="DISCOVERY",
                    managed_object=self.object,
                    op="CHANGE",
                )
                self.update_name(o)

    def send(self):
        if self.unknown_part_no:
            platform = self.object.platform
            upn = self.get_unknown_part_no()
            for pns in upn:
                # Find description
                description = "no description"
                for p in pns:
                    if p in self.pn_description:
                        description = self.pn_description[p]
                        break
                # Report error
                self.logger.error(
                    "Unknown part number for %s: %s (%s)", platform, ", ".join(pns), description
                )

    def register_unknown_part_no(
        self, vendor: "Vendor", part_no: Union[List[str], str], descripton: Optional[str]
    ):
        """
        Register missed part number
        """
        if not isinstance(part_no, list):
            part_no = [part_no]
        for p in part_no:
            if p not in self.unknown_part_no:
                self.unknown_part_no[p] = set()
            for pp in part_no:
                self.unknown_part_no[p].add(pp)
            UnknownModel.mark_unknown(vendor.code[0], self.object, p, descripton)

    def get_unknown_part_no(self) -> List[List[str]]:
        """
        Get list of missed part number variants
        """
        r = []
        for p in self.unknown_part_no:
            n = sorted(self.unknown_part_no[p])
            if n not in r:
                r += [n]
        return r

    def get_vendor(self, v: Optional[str], o_type: Optional[str] = "") -> Optional["Vendor"]:
        """
        Get vendor instance or None. Create vendor if object type is XCVR.
        """
        if v is None or v.startswith("OEM") or v == "None":
            v = "NONAME"
        v = v.upper()
        if v in self.vendors:
            return self.vendors[v]
        # Temporary fix
        if v == "D-LINK":
            v = "DLINK"
        if v == "48 47 20 47 45 4e 55 49 4e 45 00 00 00 00 00 00":
            v = "HUAWEI"
        if "INTEL" in v:
            v = "INTEL"
        if "FINISAR" in v:
            v = "FINISAR"
        o = Vendor.get_by_code(v)
        if not o and o_type == "XCVR":
            try:
                o = Vendor.ensure_vendor(v)
            except ValueError:
                self.logger.error("Vendor creating failed '%s'", v)
        self.vendors[v] = o
        return o

    def set_rule(self, rule: "ConnectionRule"):
        self.logger.debug("Setting connection rule '%s'", rule.name)
        # Compile context mappings
        self.rule_context = {}
        for ctx in rule.context:
            self.rule_context[ctx.type] = (ctx.scope, ctx.reset_scopes)
        self.logger.debug("Context mappings: %s", self.rule_context)
        # Compile rules
        for r in rule.rules:
            self.rule[r.match_type] += [r]

    def set_context(self, name: str, value: Optional[str]):
        self.ctx[name] = value
        n = "N%s" % name
        if n not in self.ctx:
            self.ctx[n] = 0
        else:
            self.ctx[n] += 1
        self.logger.debug("Set context %s = %s -> %s", name, value, str_dict(self.ctx))

    def reset_context(self, names: List[str]):
        for n in names:
            if n in self.ctx:
                del self.ctx[n]
            m = "N%s" % n
            if m in self.ctx:
                del self.ctx[m]
        self.logger.debug("Reset context scopes %s -> %s", ", ".join(names), str_dict(self.ctx))

    def find_managed(self):
        """
        Get all objects managed by managed object
        """
        self.managed = set(
            Object.objects.filter(
                data__match={
                    "interface": "management",
                    "attr": "managed_object",
                    "value": self.object.id,
                }
            ).values_list("id")
        )

    def check_management(self):
        """
        Unmanage all left objects
        """
        for oid in self.managed:
            o = Object.objects.filter(id=oid).first()
            if o:
                self.logger.info("Revoking management from %s %s", o.model.name, o.id)
                o.reset_data("management", "managed_object")
                o.save()
                o.log(
                    "Management revoked",
                    system="DISCOVERY",
                    managed_object=self.object,
                    op="CHANGE",
                )

    @staticmethod
    def is_generic_transceiver(t_name: str) -> bool:
        """
        Checking transceiver part_no can be Generic or not
        """
        return t_name and not t_name.startswith("Unknown | Transceiver")

    def get_unresolved_object_model_name(self, name: str, ff: str) -> str:
        """
        Generate unresolved object model name
        """
        if not self.is_generic_transceiver(name):
            return f"NoName | Transceiver | {ff}"
        return f"Generic | Transceiver | {ff}"

    def resolve_object(
        self,
        name: str,
        m_c: str,
        t_object: Object,
        t_c: str,
        serial: str,
        data: List[ObjectAttr],
    ) -> Optional["Object"]:
        """
        Resolve object type
        """
        # Check object is already exists
        c, object, c_name = t_object.get_p2p_connection(t_c)
        self.logger.debug("[%s] Resolve Object. Check already exists: %s", t_c, c)
        if c is not None:
            if c_name == m_c and object.get_data("asset", "serial") == serial:
                # Object with same serial number exists
                return object
            else:
                # Serial number/connection mismatch
                return None
        # Check connection type
        c = t_object.model.get_model_connection(t_c)
        if c is None:
            self.logger.error("Connection violation for %s SN %s", name, serial)
            return None  # ERROR
        # Transceiver formfactor
        tp = c.type.name.split(" | ")
        ff = tp[1]

        m = self.get_unresolved_object_model_name(name, ff)

        if m in self.unk_model:
            model = self.unk_model[m]
        else:
            model = ObjectModel.objects.filter(name=m).first()
            self.unk_model[m] = model

        if not model:
            self.logger.info("Unknown model '%s' registering unknown model", m)
            self.register_unknown_part_no(self.get_vendor("NONAME"), m, f"{name} -> {m}")
            return None
        o = Object.objects.filter(
            model=model, data__match={"interface": "asset", "attr": "serial", "value": serial}
        ).first()
        if o:
            return o
        # Create object
        self.logger.info("Creating new object. model='%s', serial='%s'", m, serial)
        data += [ObjectAttr(scope="discovery", interface="asset", attr="part_no", value=[name])]
        o = Object(
            model=model,
            data=[ObjectAttr(scope="", interface="asset", attr="serial", value=serial)] + data,
            parent=self.object.container if self.object.container else self.lost_and_found,
        )
        o.save()
        o.log(
            "Created by asset_discovery",
            system="DISCOVERY",
            managed_object=self.object,
            op="CREATE",
        )
        return o

    def get_model_map(
        self,
        vendor: str,
        part_no: Union[List[str], str],
        serial: Optional[str],
        cpe_id: Optional[str] = None,
    ) -> Optional["ObjectModel"]:
        """
        Try to resolve using model map
        """
        # Process list of part no
        if isinstance(part_no, list):
            for p in part_no:
                m = self.get_model_map(vendor, p, serial, cpe_id)
                if m:
                    return m
            return None
        for mm in ModelMapping.objects.filter(vendor=vendor, is_active=True):
            if mm.part_no and mm.part_no != part_no:
                continue
            if mm.from_serial and mm.to_serial:
                # if mm.from_serial <= serial and serial <= mm.to_serial:
                if mm.from_serial >= serial <= mm.to_serial:
                    return mm.model
            else:
                self.logger.debug("Mapping %s %s %s to %s", vendor, part_no, serial, mm.model.name)
                return mm.model
        if cpe_id:
            # Try Resolve by Generic Model
            m = f"Generic | CPE | {self.cpes[cpe_id][1].upper()}"
            self.logger.debug("Try Resolve by Generic CPE model: %s", m)
            return ObjectModel.get_by_name(m)
        return None

    def get_lost_and_found(self, object) -> Object:
        lfm = ObjectModel.objects.filter(name="Lost&Found").first()
        if not lfm:
            self.logger.error("Lost&Found model not found")
            return None
        lf = Object.objects.filter(model=lfm.id).first()
        if not lf:
            self.logger.error("Lost&Found not found")
            return None
        return lf

    def get_generic_models(self) -> List[str]:
        """ """
        return [
            om.id
            for om in ObjectModel.objects.filter(
                vendor__in=[self.generic_vendor, self.noname_vendor]
            )
        ]

    def load_cpe(self) -> Dict[str, Tuple[str, str, str, str, str]]:
        """
        Load CPE from CPE Discovery Artefacts
        """
        r = {}
        for cpe in CPE.objects.filter(
            controllers__match={"managed_object": self.object.id, "is_active": True}
        ):
            # Sync Asset
            caps = cpe.get_caps()
            if not cpe.profile.sync_asset or not caps.get("CPE | Model"):
                continue
            r[str(cpe.id)] = (
                str(cpe),
                str(cpe.type),
                caps.get("CPE | Vendor"),
                caps.get("CPE | Model"),
                caps.get("CPE | Serial Number") or cpe.global_id,
            )
        return r

    def generate_serial(self, model: ObjectModel, number: Optional[str]) -> str:
        """
        Generate virtual serial number
        """
        seed = [str(self.object.id), str(model.uuid), str(number)]
        for k in sorted(x for x in self.ctx if not x.startswith("N")):
            seed += [k, str(self.ctx[k])]
        h = hashlib.sha256(smart_bytes(":".join(seed)))
        return f"NOC{base64.b32encode(h.digest())[:7].decode('utf-8')}"

    @staticmethod
    def get_name(
        obj: Object, managed_object: Optional[Any] = None, cpe_name: Optional[str] = None
    ) -> str:
        """
        Generate discovered object's name
        """
        name = None
        if cpe_name:
            name = cpe_name
        elif managed_object:
            name = managed_object.name
            sm = obj.get_data("stack", "member")
            if sm is not None:
                # Stack member
                name += "#%s" % sm
        return name

    def disconnect_connections(self):
        for o1, o2 in self.to_disconnect:
            self.logger.info("Disconnect: %s:%s ->X<- %s", o1, o2.parent_connection, o2)
            o1.log(
                f"Disconnect {o1}:{o2.parent_connection} -> {o2}",
                system="DISCOVERY",
                managed_object=self.object,
                op="DISCONNECT",
            )
            o2.log(
                f"Disconnect {o1}:{o2.parent_connection} -> {o2}",
                system="DISCOVERY",
                managed_object=self.object,
                op="DISCONNECT",
            )
            # Move o2 to lost&found
            o2.put_into(self.lost_and_found)

    def clean_serial(self, model: "ObjectModel", number: Optional[str], serial: Optional[str]):
        # Empty value
        if not serial or serial == "None":
            new_serial = self.generate_serial(model, number)
            self.logger.info("Empty serial number. Generating virtual serial %s", new_serial)
            return new_serial
        # Too short value
        slen = len(serial)
        min_serial_size = model.get_data("asset", "min_serial_size")
        if min_serial_size is not None and slen < min_serial_size:
            new_serial = self.generate_serial(model, number)
            self.logger.info(
                "Invalid serial number '%s': Too short, must be %d symbols or more. "
                "Replacing with virtual serial %s",
                serial,
                min_serial_size,
                new_serial,
            )
            return new_serial
        # Too long value
        max_serial_size = model.get_data("asset", "max_serial_size")
        if max_serial_size is not None and slen > max_serial_size:
            new_serial = self.generate_serial(model, number)
            self.logger.info(
                "Invalid serial number '%s': Too long, must be %d symbols or less. "
                "Replacing with virtual serial %s",
                serial,
                max_serial_size,
                new_serial,
            )
            return new_serial
        # Regular expression
        serial_mask = model.get_data("asset", "serial_mask")
        if serial_mask:
            rx = self.get_serial_mask(serial_mask)
            if not rx.match(serial):
                new_serial = self.generate_serial(model, number)
                self.logger.info(
                    "Invalid serial number '%s': Must match mask '%s'. "
                    "Replacing with virtual serial %s",
                    serial,
                    serial_mask,
                    new_serial,
                )
                return new_serial
        return serial

    def sync_crossing(self, obj: Object, crossing: list[dict[str, str]] | None = None) -> None:
        """
        Synchronize crossing.
        """

        def check_port(name: str) -> None:
            x = obj.model.get_model_connection(name)
            if not x:
                msg = f"invalid connection: {x}"
                raise ValueError(msg)

        def cross_item(item: dict[str, str]) -> Crossing:
            check_port(item["input"])
            check_port(item["output"])
            return Crossing(
                input=item["input"],
                output=item["output"],
                input_discriminator=item.get("input_discrimiator"),
                output_discriminator=item.get("output_discriminator"),
                gain_db=item.get("gain_db"),
            )

        crossing = crossing or []
        self.logger.info("Set crossing: %s", crossing)
        obj.cross = [cross_item(x) for x in crossing]
        obj.save()

    @cachetools.cachedmethod(
        operator.attrgetter("_serial_masks"), lock=operator.attrgetter("_serial_masks_lock")
    )
    def get_serial_mask(self, mask):
        """
        Compile serial mask and cache value
        :param mask:
        :return:
        """
        return re.compile(mask)
