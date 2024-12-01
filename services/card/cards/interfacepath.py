# ----------------------------------------------------------------------
# interfacepath card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import codecs

#  Third-party modules
from typing import Dict, Any, List, Tuple, Set, Optional
import orjson

# NOC modules
from noc.config import config
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.core.topology.path import KSPFinder
from noc.core.topology.constraint.base import BaseConstraint
from noc.core.topology.constraint.upwards import UpwardsConstraint
from noc.core.topology.constraint.vlan import VLANConstraint
from noc.core.topology.goal.level import ManagedObjectLevelGoal
from noc.inv.models.subinterface import SubInterface
from noc.core.text import alnum_key
from noc.core.bi.decorator import bi_hash
from noc.core.clickhouse.connect import connection as ch_connection
from noc.core.clickhouse.error import ClickhouseError
from noc.core.hash import hash_str
from .base import BaseCard
from noc.core.comp import smart_text


def default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


class InterfacePathCard(BaseCard):
    name = "interfacepath"
    default_template_name = "interfacepath"
    model = Interface
    N_PATHS = 2
    SIG_LEN = 9  # odd padding to broke base64

    def get_data(self) -> Dict[str, Any]:
        r: Dict[str, Any] = {
            "object": self.object,
            "paths": [],
            "link_sets": 0,
            "if_hash": {},
            "error": None,
            "ajax_query_key": None,
        }
        mo = self.object.managed_object
        target_level = (mo.object_profile.level // 10 + 1) * 10
        try:
            finder = KSPFinder(
                mo,
                ManagedObjectLevelGoal(target_level),
                constraint=self.get_constraint(),
                n_shortest=self.N_PATHS,
            )
            for path in finder.iter_shortest_paths():
                items: List[Dict[str, Any]] = []
                ingress_links: List[List[Interface]] = [[self.object]]
                for pi in path:
                    item: Dict[str, Any] = {
                        "object": pi.start,
                        "ingress": ingress_links,
                        "egress": [],
                    }
                    ingress_links = []
                    for link in pi.links:
                        egress, ingress = self.split_interfaces(pi.start, link.interfaces)
                        ingress_links += [ingress]
                        item["egress"] += [egress]
                    if item["ingress"] == item["egress"]:
                        item["ingress"] = []
                    r["link_sets"] = max(r["link_sets"], len(item["egress"]))
                    items += [item]
                items += [{"object": pi.end, "ingress": ingress_links, "egress": []}]
                r["paths"] += [items]
        except ValueError as e:
            r["error"] = str(e)
            return r
        # Build interface hashes
        to_collect: Set[Tuple[int, int, str]] = set()
        for path in r["paths"]:
            for item in path:
                for direction in ("ingress", "egress"):
                    for link in item[direction]:
                        for iface in link:
                            ifname = iface.name
                            if ifname not in r["if_hash"]:
                                r["if_hash"][ifname] = bi_hash(ifname)
                            to_collect.add(
                                (iface.managed_object.id, iface.managed_object.bi_id, ifname)
                            )
        # @todo: Encrypt
        r["ajax_query_key"] = self.encode_query(to_collect)
        return r

    @classmethod
    def get_signature(cls, data):
        # (str) -> str
        """
        Get tamper-protection signature

        :param data: Input data
        :return: Tamper-protection signature
        """
        return smart_text(
            codecs.encode(hash_str(config.secret_key + data), "base64")[: cls.SIG_LEN]
        )

    @classmethod
    def encode_query(cls, to_collect: Set[Tuple[int, int, str]]) -> str:
        data = smart_text(
            codecs.encode(orjson.dumps(to_collect, default), "base64").replace(b"\n", b"")
        )
        return cls.get_signature(data) + data

    @classmethod
    def decode_query(cls, query: str) -> List[Tuple[int, int, str]]:
        sig, data = query[: cls.SIG_LEN], query[cls.SIG_LEN :]
        if sig != cls.get_signature(data):
            raise ValueError
        return orjson.loads(codecs.decode(data.encode(), "base64"))

    @staticmethod
    def split_interfaces(
        obj: ManagedObject, interfaces: List[Interface]
    ) -> Tuple[List[Interface], List[Interface]]:
        """
        Split list of interfaces of the links to egress (belonging to `obj`)
        and ingress (leading out of object)
        :param obj: Managed Object
        :param interfaces:  List of link interfaces
        :return: List of egress links, List of ingress links
        """
        ingress: List[Interface] = []
        egress: List[Interface] = []
        for iface in sorted(interfaces, key=lambda x: alnum_key(x.name)):
            if iface.managed_object == obj:
                egress += [iface]
            else:
                ingress += [iface]
        return egress, ingress

    @staticmethod
    def humanize_metric(value: str) -> str:
        if not value or value == "\\N":
            return "-"
        cv = float(value)
        for t, n in [(1000000000, "G"), (1000000, "M"), (1000, "k")]:
            if cv >= t:
                if cv // t * t == cv:
                    return "%d%s" % (cv // t, n)
                else:
                    return "%.2f%s" % (float(cv) / t, n)
        return str(cv)

    def get_ajax_data(self, **kwargs):
        # Parse query params
        query: List[Tuple[int, int, str]] = self.decode_query(self.handler.get_argument("key"))
        # Get metrics
        from_ts = datetime.datetime.now() - datetime.timedelta(seconds=1800)
        from_ts = from_ts.replace(microsecond=0)
        interface_sql = """
          SELECT
            managed_object,
            path[4] AS iface,
            argMax(load_in, ts) AS load_in,
            argMax(load_out, ts) AS load_out,
            argMax(packets_in, ts) AS packets_in,
            argMax(packets_out, ts) AS packets_out,
            argMax(errors_in, ts) AS errors_in,
            argMax(errors_out, ts) AS errors_out
          FROM interface
          WHERE
            date >= toDate('%s')
            AND ts >= toDateTime('%s')
            AND (%s)
          GROUP BY managed_object, iface
        """ % (
            from_ts.date().isoformat(),
            from_ts.isoformat(sep=" "),
            " OR ".join(
                "(managed_object=%d AND path[4]='%s')" % (q[1], q[2].replace("'", "''"))
                for q in query
            ),
        )
        # Get data
        metrics: List[Tuple[int, str, str, str, str, str]] = []
        ch = ch_connection()
        try:
            for (
                mo,
                iface,
                load_in,
                load_out,
                packets_in,
                packets_out,
                errors_in,
                errors_out,
            ) in ch.execute(post=interface_sql):
                if_hash = str(bi_hash(iface))
                metrics += [
                    # (mo, if_hash, "speed", self.humanize_metric(speed)),
                    (mo, if_hash, "load_in", self.humanize_metric(load_in)),
                    (mo, if_hash, "load_out", self.humanize_metric(load_out)),
                    (mo, if_hash, "packets_in", self.humanize_metric(packets_in)),
                    (mo, if_hash, "packets_out", self.humanize_metric(packets_out)),
                    (mo, if_hash, "errors_in", self.humanize_metric(errors_in)),
                    (mo, if_hash, "errors_out", self.humanize_metric(errors_out)),
                ]
        except ClickhouseError:
            pass
        # Set defaults
        m_index: Set[Tuple[int, str]] = set()
        for mo_bi_id, iface, _, _ in metrics:
            m_index.add((int(mo_bi_id), iface))
        interface_metrics = {
            "speed",
            "load_in",
            "load_out",
            "packets_in",
            "packets_out",
            "errors_in",
            "errors_out",
        }
        for _, mo_bi_id, iface in query:
            if (int(mo_bi_id), str(bi_hash(iface))) not in m_index:
                for metric in interface_metrics:
                    metrics += [(str(mo_bi_id), str(bi_hash(iface)), metric, "-")]
        # managed object id -> bi id
        mo_map: Dict[int, int] = {q[0]: q[1] for q in query}
        # Get interface statuses
        for doc in Interface._get_collection().find(
            {"$or": [{"managed_object": q[0], "name": q[2]} for q in query]},
            {
                "_id": 0,
                "managed_object": 1,
                "name": 1,
                "admin_status": 1,
                "oper_status": 1,
                "in_speed": 1,
                "out_speed": 1,
                "full_duplex": 1,
            },
        ):
            mo = str(mo_map[doc["managed_object"]])
            if_hash = str(bi_hash(doc["name"]))
            status = 0
            if "admin_status" in doc and doc["admin_status"]:
                status = 2 if doc["oper_status"] else 1
            duplex = "-"
            if "full_duplex" in doc:
                duplex = "Full" if doc["full_duplex"] else "Half"
            speed = "-"
            if "in_speed" in doc:
                speed = self.humanize_metric(doc["in_speed"] * 1000)
            metrics += [
                (mo, if_hash, "speed", speed),
                (mo, if_hash, "duplex", duplex),
                (mo, if_hash, "status", status),
            ]
        # Get current object statuses
        obj_statuses = ManagedObject.get_statuses(list(mo_map))
        statuses = {str(mo_map[mo_id]): obj_statuses.get(mo_id, True) for mo_id in obj_statuses}
        return {"metrics": metrics, "statuses": list(statuses.items())}

    def get_constraint(self) -> Optional[BaseConstraint]:
        """
        Get optional path constraint
        :return:
        """
        constraint = UpwardsConstraint()
        for doc in SubInterface._get_collection().find(
            {"interface": self.object.id}, {"_id": 0, "enabled_afi": 1, "untagged_vlan": 1}
        ):
            if doc and "BRIDGE" in doc["enabled_afi"] and doc.get("untagged_vlan"):
                constraint &= VLANConstraint(vlan=doc["untagged_vlan"], strict=False)
                break
        return constraint
