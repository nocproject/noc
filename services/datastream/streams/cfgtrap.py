# ----------------------------------------------------------------------
# cfgtrap datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.base import DataStream
from noc.core.diagnostic.hub import SNMPTRAP_DIAG
from noc.main.models.pool import Pool
from noc.main.models.remotesystem import RemoteSystem
from noc.main.models.label import Label
from noc.wf.models.state import State
from noc.sa.models.managedobject import ManagedObject


class CfgTrapDataStream(DataStream):
    name = "cfgtrap"
    DIAGNOSTIC = SNMPTRAP_DIAG
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        mo = ManagedObject.objects.filter(id=id).values_list(
            "id",
            "name",
            "bi_id",
            "state",
            "pool",
            "fm_pool",
            "administrative_domain",
            "administrative_domain__name",
            "administrative_domain__remote_system",
            "administrative_domain__remote_id",
            "remote_system",
            "remote_id",
            "address",
            "labels",
            "effective_labels",
            "trap_community",
            "trap_source_ip",
            "trap_source_type",
            "event_processing_policy",
            "object_profile__event_processing_policy",
            "object_profile__trapcollector_storm_policy",
            "object_profile__trapcollector_storm_threshold",
        )[:1]
        if not mo:
            raise KeyError()
        (
            mo_id,
            name,
            bi_id,
            state,
            pool,
            fm_pool,
            adm_domain,
            adm_domain_name,
            adm_domain_remote_system,
            adm_domain_remote_id,
            remote_system,
            remote_id,
            address,
            labels,
            effective_labels,
            trap_community,
            trap_source_ip,
            trap_source_type,
            event_processing_policy,
            mop_event_processing_policy,
            mop_trapcollector_storm_policy,
            mop_trapcollector_storm_threshold,
        ) = mo[0]
        # Process event policy
        state = State.get_by_id(state)
        if (
            not state.is_enabled_interaction("ALARM")
            or (str(event_processing_policy) == "P" and str(mop_event_processing_policy) != "E")
            or str(event_processing_policy) == "D"
            or str(trap_source_type) == "d"
        ):
            raise KeyError("Disabled by trap source ManagedObject")
        # Process trap sources
        pool = str(Pool.get_by_id(pool).name)
        r = {
            "id": str(mo_id),
            "pool": pool,
            "fm_pool": str(Pool.get_by_id(fm_pool).name) if fm_pool else pool,
            "addresses": [],
            "trap_community": trap_community,
            "managed_object": {
                "id": str(mo_id),
                "bi_id": str(bi_id),
                "name": name,
                "administrative_domain": {"id": adm_domain, "name": adm_domain_name},
                "labels": [
                    cls.qs(ll)
                    for ll in Label.objects.filter(
                        name__in=labels, expose_datastream=True
                    ).values_list("name")
                ],
            },
            "effective_labels": effective_labels,
            "name": name,
            "bi_id": bi_id,
            "storm_policy": mop_trapcollector_storm_policy,
            "storm_threshold": mop_trapcollector_storm_threshold,
        }
        if remote_system:
            rs = RemoteSystem.get_by_id(remote_system)
            r["managed_object"]["remote_system"] = {"id": str(rs.id), "name": rs.name}
            r["managed_object"]["remote_id"] = remote_id
        if adm_domain_remote_system:
            rs = RemoteSystem.get_by_id(adm_domain_remote_system)
            r["managed_object"]["administrative_domain"]["remote_system"] = {
                "id": str(rs.id),
                "name": rs.name,
            }
            r["managed_object"]["administrative_domain"]["remote_id"] = adm_domain_remote_id
        if str(trap_source_type) == "m" and address:
            r["addresses"] += [str(address)]
        elif str(trap_source_type) == "s" and trap_source_ip:
            r["addresses"] = [str(trap_source_ip)]
        elif trap_source_type == "l":
            # Loopback address
            r["addresses"] = cls._get_loopback_addresses(mo_id)
            if not r["addresses"]:
                raise KeyError("No Loopback interface with address")
        elif trap_source_type == "a":
            # All interface addresses
            r["addresses"] = cls._get_all_addresses(mo_id)
            if not r["addresses"]:
                raise KeyError("No interfaces with IP")
        else:
            raise KeyError(f"Unsupported Trap Source Type: {trap_source_type}")
        return r

    @classmethod
    def _get_loopback_addresses(cls, mo_id):
        from noc.inv.models.interface import Interface
        from noc.inv.models.subinterface import SubInterface

        # Get all loopbacks
        if_ids = []
        for d in Interface._get_collection().find(
            {"managed_object": int(mo_id), "type": "loopback"}, {"_id": 1}
        ):
            if_ids += [d["_id"]]
        if not if_ids:
            return []
        # Get loopback's addresses
        r = []
        for d in SubInterface._get_collection().find(
            {
                "managed_object": int(mo_id),
                "interface": {"$in": if_ids},
                "ipv4_addresses": {"$exists": True},
            },
            {"_id": 0, "ipv4_addresses": 1},
        ):
            for a in d.get("ipv4_addresses", []):
                r += [str(a).split("/")[0]]
        return r

    @classmethod
    def _get_all_addresses(cls, mo_id):
        from noc.inv.models.subinterface import SubInterface

        r = []
        for d in SubInterface._get_collection().find(
            {"managed_object": int(mo_id), "ipv4_addresses": {"$exists": True}}, {"ipv4_addresses"}
        ):
            for a in d.get("ipv4_addresses", []):
                r += [str(a).split("/")[0]]
        return r

    @classmethod
    def get_meta(cls, data):
        return {"pool": data.get("pool")}

    @classmethod
    def filter_pool(cls, name):
        return {f"{cls.F_META}.pool": name}
