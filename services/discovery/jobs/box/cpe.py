# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# ID check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.objectmodel import ObjectModel
from noc.inv.models.object import Object
from noc.sa.models.profile import Profile


class CPECheck(DiscoveryCheck):
    """
    CPE check
    @todo: Remove stale CPE
    """
    name = "cpe"
    required_script = "get_cpe"
    required_capabilities = ["Mobile | BSC"]

    def handler(self):
        pop_mod = ObjectModel.objects.get(name="PoP | Core")
        cont = Object.objects.get(name="Казань")
        co_id = self.object.id
        self.logger.info("Checking CPEs")
        now = datetime.datetime.now()
        result = self.object.scripts.get_cpe()
        for cpe in result:
            mo = self.find_cpe(cpe["global_id"], co_id)
            mo2 = self.find_cpe2(cpe["id"], co_id)
            if mo:
                if mo == cpe["name"]:
                    changes = self.update_if_changed(mo, {
                        "controller": self.object,
                        "local_cpe_id": cpe["id"],
                        "global_cpe_id": cpe["global_id"],
                        "address": cpe["ip"],
                        "description": cpe["description"],
                        "last_seen": now
                    })
                    if changes:
                        self.logger.debug(
                            "[%s|%s] Changed: %s",
                            cpe["id"], cpe["global_id"],
                            ", ".join("%s='%s'" % c for c in changes)
                        )
                else:
                    changes = self.update_if_changed(mo, {
                        "name": cpe["name"],
                        "controller": self.object,
                        "local_cpe_id": cpe["id"],
                        "global_cpe_id": cpe["global_id"],
                        "address": cpe["ip"],
                        "description": cpe["description"],
                        "last_seen": now
                    })
                    if changes:
                        self.logger.debug(
                            "[%s|%s] Changed: %s",
                            cpe["id"], cpe["global_id"],
                            ", ".join("%s='%s'" % c for c in changes)
                        )
            elif mo2:
                if mo2 == cpe["name"]:
                    changes = self.update_if_changed(mo2, {
                        "controller": self.object,
                        "local_cpe_id": cpe["id"],
                        "global_cpe_id": cpe["global_id"],
                        "address": cpe["ip"],
                        "description": cpe["description"],
                        "last_seen": now
                    })
                    if changes:
                        self.logger.debug(
                            "[%s|%s] Changed: %s",
                            cpe["id"], cpe["global_id"],
                            ", ".join("%s='%s'" % c for c in changes)
                        )
                else:
                    changes = self.update_if_changed(mo2, {
                        "name": cpe["name"],
                        "controller": self.object,
                        "local_cpe_id": cpe["id"],
                        "global_cpe_id": cpe["global_id"],
                        "address": cpe["ip"],
                        "description": cpe["description"],
                        "last_seen": now
                    })
                    if changes:
                        self.logger.debug(
                            "[%s|%s] Changed: %s",
                            cpe["id"], cpe["global_id"],
                            ", ".join("%s='%s'" % c for c in changes)
                        )
            else:
                name = cpe.get("name") or (cpe.get("name") + "(" + self.object.name + ")")
                if ManagedObject.objects.filter(name=name).exists():
                    name = cpe.get("name") + "(" + self.object.name + ")"
                self.logger.info(
                    "[%s|%s] Created CPE %s",
                    cpe["id"], cpe["global_id"], name
                )
                # point_model = ObjectModel.objects.get(name="PoP | Access")
                mo = ManagedObject(
                    name=name,
                    pool=self.object.pool,
                    profile=Profile.objects.get(name="Generic.Host"),
                    object_profile=self.object.object_profile.cpe_profile or self.object.object_profile,
                    administrative_domain=self.object.administrative_domain,
                    scheme=self.object.scheme,
                    segment=self.object.segment,
                    auth_profile=self.object.object_profile.cpe_auth_profile or self.object.auth_profile,
                    address=cpe.get("ip"),
                    controller=self.object,
                    local_cpe_id=cpe["id"],
                    global_cpe_id=cpe["global_id"],
                    description=cpe["description"],
                    last_seen=now,
                    tt_system=self.object.tt_system,
                    tt_queue=self.object.tt_queue

                )
                mo.save()

        for cpe in result:
            mo = self.find_cpe(cpe["global_id"], co_id)
            """
            cpedata = {
                "controller": self.object,
                "local_cpe_id": cpe["id"],
                "global_cpe_id": cpe["id"]
            }
            """
            if mo:
                vendor = mo.get_attr("vendor")
                if not vendor:
                    if "serial" in cpe:
                        mo.set_attr("Serial Number", cpe["serial"])
                    if "vendor" in cpe:
                        mo.set_attr("vendor", cpe["vendor"])
                    if "platform" in cpe:
                        mo.set_attr("platform", cpe["platform"])
                    if "model" in cpe:
                        mo.set_attr("model", cpe["model"])
                    if "swverdld" in cpe:
                        mo.set_attr("swverdld", cpe["swverdld"])
                    if "swveract" in cpe:
                        mo.set_attr("swveract", cpe["swveract"])
                    if "swverrepl" in cpe:
                        mo.set_attr("swverrepl", cpe["swverrepl"])
                    if "tmode" in cpe:
                        mo.set_attr("tmode", cpe["tmode"])
                    if mo.set_attr:
                        self.logger.debug(
                            "[%s|%s] Add: %s",
                            cpe["id"], cpe["global_id"],
                            ", ".join("%s='%s'" % c for c in changes)
                        )
                if "csystype" in cpe:
                    cd = mo.get_caps()
                    cd["Mobile | Sector | Band"] = cpe["csystype"]
                    mo.update_caps(cd, "cpe")
                if "type" in cpe:
                    cd = mo.get_caps()
                    if cpe["type"] == "bs":
                        cd["Mobile | BS"] = True
                        mo.update_caps(cd, "cpe")
                        if mo.container is None:
                            pop = Object(model=pop_mod, name=mo.name, container=cont.id)
                            pop.save()
                            self.logger.info("Create PoP | Access %s for mo %s" % (pop, mo.name))
                            mo.container = pop
                            mo.save()
                            self.logger.info("Add PoP | Access %s for mo %s" % (pop, mo.name))
                        else:
                            self.logger.debug("MO %s have container %s" % (mo.name, mo.container))
                            pass
                    if cpe["type"] == "st":
                        cd = mo.get_caps()
                        cd["Mobile | Sector"] = True
                        mo.update_caps(cd, "cpe")
                        if mo.container is None:
                            co = None
                            for co in ManagedObject.objects.filter(is_managed=True, local_cpe_id=mo.name.split("#")[0],
                                                                   controller=co_id):
                                if not co:
                                    self.logger.info("Not CO for %s" % mo.name)
                                    continue
                                else:
                                    mo.container = co.container
                                    mo.save()
                                    self.logger.info("Containder  %s add for mo %s" % (co.container, mo.name))
                        else:
                            self.logger.debug("MO %s have container %s" % (mo.name, mo.container))
                            pass

            else:
                continue

    @classmethod
    def find_cpe(cls, global_id, co_id):
        try:
            return ManagedObject.objects.get(is_managed=True, global_cpe_id=global_id, controller=co_id)
        except ManagedObject.DoesNotExist:
            return None

    @classmethod
    def find_cpe2(cls, local_cpe_id, co_id):
        try:
            return ManagedObject.objects.get(is_managed=True, local_cpe_id=local_cpe_id, controller=co_id)
        except ManagedObject.DoesNotExist:
            return None
