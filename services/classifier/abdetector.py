# ----------------------------------------------------------------------
# AbductDetector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Tuple, List, Dict

# NOC modules
from noc.inv.models.interface import Interface


class AbductDetector(object):
    def __init__(self):
        self.active: Dict[int, List[Tuple[int, str]]] = {}

    def register_up(self, ts: int, interface: Interface):
        """
        Register link up

        :param ts: Event timestamp
        :param interface:
        :return:
        """
        mo = interface.managed_object
        items = self.active.get(mo.id)
        if items is None:
            return
        name = interface.name
        items = [i for i in items if i[0] > ts and i[1] != name]
        if not items:
            # Free memory
            del self.active[mo.id]
        else:
            self.active[mo.id] = items

    def register_down(self, ts: int, interface: Interface) -> bool:
        """
        Register link down

        :param ts: Event timestamp
        :param interface:
        :return: True, if massive outage detected
        """
        mo = interface.managed_object
        items = self.active.get(mo.id) or []
        name = interface.name
        items = [i for i in items if i[0] > ts and i[1] != name]
        items.append((ts + mo.object_profile.abduct_detection_window, name))
        self.active[mo.id] = items
        return len(items) >= mo.object_profile.abduct_detection_threshold
