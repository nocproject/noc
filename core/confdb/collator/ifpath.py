# ----------------------------------------------------------------------
# IfPathCollator
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
import logging

# NOC modules
from .base import BaseCollator
from typing import Tuple, List, Union, Set

IFTYPE_SPLITTER = " "
IFPATH_SPLITTER = "/"

rx_iftype_detect = re.compile(r"([a-zA-Z_]+)(\d+)")

rx_ifname_splitter = re.compile(r"^(\d*\D+)??(\d+[/:])*(\d+)$")
rx_ifpath_splitter = re.compile(r"(\d+)")

logger = logging.getLogger(__name__)


class IfPathCollator(BaseCollator):
    """
    Direct map between connection name and interface name by it path.
    1) - split SA interface name on path_component by name_path method
    2) - iterate over component on Inventory Item path from end to start
    3) - Compare SA path and Inventory item path by component. If equal - return interface
    4) - If more that one interfaces has equal path, but different if_type, use protocols for detect right
    """

    def __init__(self, profile=None):
        super().__init__(profile)
        self.paths = defaultdict(list)

    PROTOCOL_MAPPING = {
        "et": {
            "1000BASET",
            "1000BASETX",
            "100BASETX",
            "10BASET",
            "TransEth100M",
            "TransEth1G",
            "TransEth10G",
        },  # Ethernet
        "me": {"10BASET", "100BASETX"},
        "m-": {"10BASET", "100BASETX"},
        "fa": {"100BASETX", "10BASET", "TransEth100M"},  # FastEthernet
        "fo": {"TransEth40G"},  # FortyGigabitEthernet
        "gi": {
            "1000BASET",
            "1000BASETX",
            "TransEth1G",
        },  # GigabitEthernet
        "te": {"TransEth10G"},  # TenGigabitEthernet
        "xg": {"TransEth10G"},
    }

    # TransEth1G,TransEth10G
    def get_protocols(self, if_name: str) -> Set[str]:
        """
        Getting protocols by ifname.
        :param if_name: Interface name
        :return:
        """
        return self.PROTOCOL_MAPPING.get(if_name.lower()[:2])

    @staticmethod
    def name_path(if_name: str) -> Tuple[Union[str, None], List[str], Union[str, None]]:
        """
        Split Interface Name by path component: if_type, if_path, if_num.
         Example Gi 1/0/2: if_type: Gi, if_path: 1/0, if_num: 2;
         10: if_type: None, if_path: [], if_num: 10
        :param if_name:
        :return:
        """
        match = rx_ifname_splitter.match(if_name)
        if not match:
            return None, [], None
        if_type, if_path, if_num = match.groups()
        if if_path:
            if_path = rx_ifpath_splitter.findall(
                if_name[match.end(1) if match.group(1) else 0 : match.start(3)]
            )
        return if_type, if_path or [], if_num

    def iter_path_component(self, path) -> str:
        """
        Iterator by path_component in PathItem. Return path component from end to start
        :param path:
        :return:
        """
        if not path:
            return None
        for item in reversed(path):
            _, c_path, c_num = self.name_path(item.connection.name)
            yield c_num
            # if len(c_path) > 2:
            #     # Remove first element
            #     # c_path.pop(0)
            #     # Absolute path
            #     logger.warning("On slot name use absolute path. Strip first")
            #     c_path = c_path[1:]
            for cp in reversed(c_path):
                if not cp.isdigit():
                    # if not number - skipping (X/1/1)
                    logger.warning("Path component '%s' is not digit. Skipping..", cp)
                    continue
                yield cp
        if item.object.get_data("stack", "stackable"):
            yield item.object.get_data("stack", "member")

    def collate(self, physical_path, interfaces):
        logger.debug("Check physical path: %s", physical_path)
        if not self.paths:
            # SA interface path map
            for if_name, iface in interfaces.items():
                if iface.type not in {"physical", "management"}:
                    # Physical scope
                    continue
                if_type, if_path, if_num = self.name_path(if_name)
                if not if_num and not if_type:
                    logger.warning("Not matched ifpath format ifname")
                    continue
                protocols = self.get_protocols(if_type)
                # self.paths[tuple(if_path) or None][if_num].append((if_type, if_name, protocols))
                self.paths[if_num] += [(tuple(if_path), if_name, protocols)]
            logger.debug("Paths mapping %s", self.paths)
        paths_candidate = []

        if_type, if_path, if_num = self.name_path(physical_path[-1].connection.name)
        if if_num not in self.paths:
            logger.warning("Interface number %s is not in SA paths", if_num)
            return None

        if physical_path[:-1]:
            # slot devices
            candidates = [x for x in self.paths[if_num]]
            for step, num in enumerate(self.iter_path_component(physical_path)):
                if not step:
                    continue
                candidates = [
                    x
                    for x in candidates
                    if (len(x[0]) < step) or (len(x[0]) >= step and x[0][-step] == num)
                ]

            if candidates:
                paths_candidate.append(tuple(candidates[0][0]))

        if if_path and physical_path[0].object.get_data("stack", "member"):
            # @todo perhaps move to other collator
            paths_candidate.append(
                tuple([physical_path[0].object.get_data("stack", "member")] + if_path[1:])
            )
        elif if_path:
            paths_candidate.append(tuple(if_path))
            # print(physical_path[0].object.get_data("stack", "member"))
            # paths_candidate.append(tuple(reversed(tuple(self.iter_path_component([physical_path[-1]]))[1:])))

        logger.debug(
            "Path candidates: %s, protocols: %s, (stack %s)",
            paths_candidate,
            physical_path[-1].connection.protocols,
            physical_path[0].object.get_data("stack", "member"),
        )
        if_proto = set(physical_path[-1].connection.protocols)
        for p, if_name, protocols in self.paths[if_num]:
            if p in paths_candidate:
                if not protocols or not if_proto.intersection(protocols):
                    # Protocols used for filter iface_type with equal path
                    # @todo empty protocols
                    logger.info("Interface proto not coverage models: %s:%s", if_proto, protocols)
                    continue
                # self.paths[if_num].remove((p, if_name, protocols))
                return if_name
            elif not paths_candidate and len(self.paths[if_num]):
                # USe for if_num only format
                # self.paths[if_num].remove((p, if_name, protocols))
                return if_name

        return None
