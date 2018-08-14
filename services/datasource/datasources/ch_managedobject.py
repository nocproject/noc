# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CHManagedObject datasource
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseDataSource
from noc.main.models.remotesystem import RemoteSystem
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.profile import Profile
from noc.inv.models.platform import Platform
from noc.inv.models.firmware import Firmware
# from noc.lib.app.reportdatasources.report_container import ReportContainerData


class CHManagedObjectDataSource(BaseDataSource):
    name = "ch_managedobject"

    def extract(self):
        # containers = ReportContainerData(list(ManagedObject.objects.all().order_by(
        #     "container").values_list("container", flat=True)))
        # containers = containers.get_dictionary()
        for (mo_id, bi_id, name, address, profile,
             platform, version, remote_id, remote_system,
             adm_id, adm_name, container) in \
                ManagedObject.objects.all().order_by("id").values_list(
                    "id", "bi_id", "name", "address", "profile",
                    "platform", "version", "remote_id", "remote_system",
                    "administrative_domain", "administrative_domain__name", "container"):
            yield (
                bi_id,
                mo_id,
                name,
                address,
                Profile.get_by_id(profile).name if profile else "",
                Platform.get_by_id(platform).name if platform else "",
                Firmware.get_by_id(version).version if version else "",
                remote_id if remote_id else "",
                RemoteSystem.get_by_id(remote_system).name if remote_system else "",
                adm_id,
                adm_name,
                # containers.get(container, ("",))[0] if container else ("",)
                ""
            )
