# ----------------------------------------------------------------------
#  Interface event handlers
# ----------------------------------------------------------------------
#  Copyright (C) 2007-2021 The NOC Project
#  See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import datetime
import time

# NOC modules
from noc.inv.models.interface import Interface
from noc.core.validators import is_float
from noc.core.pm.utils import get_interface_metrics

logger = logging.getLogger(__name__)


def th_interval(mo, event):
    periodic_interval = mo.object.object_profile.periodic_discovery_interval
    if event["window_type"] == "m":
        threshold_interval = int(periodic_interval) * int(event["window"])
    else:
        threshold_interval = int(event["window"])
    return int(threshold_interval) / 60


def grafana_date():
    # Date Time Block
    from_date = datetime.datetime.now() - datetime.timedelta(hours=6)
    date_limit = datetime.datetime.now() - datetime.timedelta(days=6)
    # interval = (to_date - from_date).days
    ts_from_date = time.mktime(from_date.timetuple())
    ts_date_limit = time.mktime(date_limit.timetuple())
    ts_from_date = max(ts_from_date, ts_date_limit)
    return str(int(ts_from_date * 1000))


def handler(mo, event):
    iface_name = event["path"].split("|")[-1::][0].split("::")[-1].strip()
    iface = Interface.objects.get(name=iface_name, managed_object=mo.object)
    try:
        event["interface"] = iface_name
        if iface.description:
            event["description"] = str(iface.description)
        event["profile"] = str(iface.profile.name)
        event["threshold_interval"] = th_interval(mo, event)
        event["ts_from_date"] = grafana_date()
        if "Duplex" in event["metric"]:
            if event["value"] != 2:
                logger.debug("Value %s is not True" % event["value"])
                return None
        if "Status" in event["metric"]:
            if "Admin" in event["metric"]:
                if iface.is_linked:
                    linked_object = iface.link.interfaces
                    if linked_object and len(linked_object) == 2:
                        linked_object.remove(iface)
                        event["linked_object"] = linked_object[0].managed_object.name
                        event["linked_object_interface"] = linked_object[0].name
                        event["linked_object_status"] = linked_object[0].managed_object.get_status()
            else:
                ifaces_metrics, last_ts = get_interface_metrics(mo.object)
                im = ifaces_metrics[mo.object][iface_name]
                error_in = im.get("Interface | Errors | In")
                error_out = im.get("Interface | Errors | Out")
                if error_in is not None:
                    event["error_in"] = error_in
                if error_out is not None:
                    event["error_out"] = error_out
                if iface.is_linked:
                    linked_object = iface.link.interfaces
                    if linked_object and len(linked_object) == 2:
                        linked_object.remove(iface)
                        event["linked_object"] = linked_object[0].managed_object.name
                        event["linked_object_interface"] = linked_object[0].name
                        event["linked_object_status"] = linked_object[0].managed_object.get_status()
                        linked_ifaces_metrics, linked_last_ts = get_interface_metrics(
                            linked_object[0].managed_object
                        )
                        if linked_ifaces_metrics:
                            lim = linked_ifaces_metrics[linked_object[0].managed_object][
                                linked_object[0].name
                            ]
                            linked_error_in = lim.get("Interface | Errors | In")
                            linked_error_out = lim.get("Interface | Errors | Out")
                            if linked_error_in is not None:
                                event["linked_error_in"] = linked_error_in
                            if linked_error_out is not None:
                                event["linked_error_out"] = linked_error_out
        if "Errors" in event["metric"]:
            if iface.is_linked:
                linked_object = iface.link.interfaces
                if linked_object and len(linked_object) == 2:
                    linked_object.remove(iface)
                    event["linked_object"] = linked_object[0].managed_object.name
                    event["linked_object_interface"] = linked_object[0].name
        if is_float(event["value"]):
            event["value"] = round(float(event["value"]), 2)
        return event
    except Exception as e:
        logger.info("Error: %s \n %s", e, iface_name)
        return event


def handler_object(mo, event):
    try:
        event["threshold_interval"] = th_interval(mo, event)
        event["ts_from_date"] = grafana_date()
        res = event["path"].split("|")
        if len(res) > 2:
            event["name"] = res[-1::][0].split("::")[-1]
        if is_float(event["value"]):
            event["value"] = round(float(event["value"]), 2)
        return event
    except Exception as e:
        logger.info("Error: %s \n %s", e, event["path"].split("|")[-1::][0].split("::")[-1].strip())
        return event
