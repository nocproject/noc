# ----------------------------------------------------------------------
# CHInterfaceAttributes datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from pymongo import ReadPreference

# NOC modules
from .base import BaseDataSource
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.interface import Interface
from noc.inv.models.interfaceprofile import InterfaceProfile


class CHInterfaceAttributesDataSource(BaseDataSource):
    name = "ch_interfaceattributes"

    def extract(self):
        mos_id = dict(ManagedObject.objects.filter().values_list("id", "bi_id"))
        iface_prof = {
            i[0]: (i[1], int(i[2] or 0))
            for i in InterfaceProfile.objects.filter().values_list("id", "name", "is_uni")
        }
        ifs = Interface._get_collection().with_options(
            read_preference=ReadPreference.SECONDARY_PREFERRED
        )
        for iface in ifs.find(
            {"type": "physical"},
            {
                "_id": 0,
                "managed_object": 1,
                "name": 1,
                "description": 1,
                "profile": 1,
                "in_speed": 1,
            },
        ).sort("managed_object"):
            yield (
                mos_id[iface["managed_object"]],
                iface["name"],
                iface.get("description", ""),
                iface_prof[iface["profile"]][0],
                abs(iface.get("in_speed", 0)) * 1000,  # iface speed in kbit/s convert to bit/s,
                # some vendors set speed -1 for iface down
                iface_prof[iface["profile"]][1],
            )
