# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# address datastream
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.datastream.base import DataStream
from noc.ip.models.address import Address


def qs(s):
    if not s:
        return ""
    return s.encode("utf-8")


class AddressDataStream(DataStream):
    name = "address"
    clean_id = DataStream.clean_id_int

    @classmethod
    def get_object(cls, id):
        address = Address.objects.filter(id=id).first()
        if not address:
            raise KeyError()
        r = {
            "id": str(address.id),
            "name": qs(address.name),
            "address": str(address.address),
            "afi": "ipv%s" % address.afi,
            "source": address.source,
        }
        if address.description:
            r["description"] = str(address.description)
        if address.tags:
            r["tags"] = [qs(x) for x in address.tags]
        if address.fqdn:
            r["fqdn"] = qs(address.fqdn)
        if address.mac:
            r["mac"] = str(address.mac)
        if address.subinterface:
            r["subinterface"] = qs(address.subinterface)
        cls._apply_state(address, r)
        cls._apply_profile(address, r)
        cls._apply_vrf(address, r)
        cls._apply_project(address, r)
        return r

    @staticmethod
    def _apply_state(address, r):
        r["state"] = {
            "id": str(address.state.id),
            "name": qs(address.state.name),
            "workflow": {
                "id": str(address.state.workflow.id),
                "name": qs(address.state.workflow.name),
            },
        }
        if address.allocated_till:
            r["state"]["allocated_till"] = address.allocated_till.isoformat()

    @staticmethod
    def _apply_profile(address, r):
        r["profile"] = {"id": str(address.profile.id), "name": qs(address.profile.name)}

    @staticmethod
    def _apply_project(address, r):
        if not address.project:
            return
        r["project"] = {"id": str(address.project.id), "name": qs(address.project.name)}

    @staticmethod
    def _apply_vrf(address, r):
        if not address.vrf or address.vrf.is_global:
            return
        r["vrf"] = {"id": str(address.vrf.id), "name": str(address.vrf.name)}
