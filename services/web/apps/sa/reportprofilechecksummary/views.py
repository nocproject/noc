# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------
# sa.reportprofilechecksummary
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""

from noc.lib.app.simplereport import SimpleReport, SectionRow, PredefinedReport
from noc.lib.nosql import get_db
from pymongo import ReadPreference
from noc.main.models.pool import Pool
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.managedobjectprofile import ManagedObjectProfile
from noc.sa.models.useraccess import UserAccess
from noc.core.translation import ugettext as _


class ReportFilterApplication(SimpleReport):
    title = _("Managed Object Profile Check Summary")
    predefined_reports = {
        "default": PredefinedReport(
            _("Managed Object Profile Check Summary"), {}
        )
    }

    def get_data(self, request, **kwargs):
        data = []
        summary = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        s1 = ["1.1", "1.2", "1.2.1", "1.2.1.1", "1.2.2", "1.2.2.1", "1.2.2.2",
              "1.2.2.2.1", "1.2.2.2.2", "1.2.2.2.2.1", "1.2.2.2.2.2", "1.2.2.2.2.3", "1.2.2.2.2.4"]

        for p in Pool.objects.order_by("name"):
            if p.name == "P0001":
                continue
            data += [SectionRow(name=p.name)]

            # Managed Object Profile w disabled ping
            mnp_in = list(ManagedObjectProfile.objects.filter(enable_ping=False))
            # Managed Object Profile w disabled box profile
            mnp_wobox_in = list(ManagedObjectProfile.objects.filter(enable_ping=True, enable_box_discovery=False))

            # Is Managed MO exclude ping disabled
            is_managed = ManagedObject.objects.filter(is_managed=True, pool=p).exclude(object_profile__in=mnp_in)
            # Is Not Managed MO
            is_not_man = ManagedObject.objects.filter(is_managed=False, pool=p)
            # MO w disabled ping profile
            is_not_resp = ManagedObject.objects.filter(is_managed=True, pool=p, object_profile__in=mnp_in)
            # MO w disable box profile
            is_box_dis = ManagedObject.objects.filter(is_managed=True, pool=p, object_profile__in=mnp_wobox_in)

            if not request.user.is_superuser:
                # UserRights Filtering
                is_managed = is_managed.filter(administrative_domain__in=UserAccess.get_domains(request.user))
                is_not_man = is_not_man.filter(administrative_domain__in=UserAccess.get_domains(request.user))
                is_not_resp = is_not_resp.filter(administrative_domain__in=UserAccess.get_domains(request.user))

            # Managed w defined profile (not Generic.Host)
            is_managed_not_generic = is_managed.exclude(profile_name="Generic.Host")
            # Managed w undefined profile (Generic.Host)
            is_managed_undef = is_managed.filter(profile_name="Generic.Host")

            is_managed_undef_in = list(is_managed_undef.values_list("id", flat=True))
            is_managed_not_generic_in = list(is_managed_not_generic.values_list("id", flat=True))

            is_managed_c = is_managed.count()
            is_managed_not_generic_c = len(is_managed_not_generic_in)

            if not (is_managed.count and is_managed_not_generic_c):
                # @todo Если unmanaged != 0 - выводить только его (разбить на is_managed и is_unmanaged
                data.pop()
                continue

            if not is_managed_c:
                data += [["", "Has not permissions to view", None]]
                continue

            # is_alive = [s.id for s in is_managed if s.get_status()]
            is_alive_id = get_db()["noc.cache.object_status"].find({"object": {"$in": is_managed_undef_in},
                                                                    "status": True},
                                                                   {"_id": 1, "object": 1},
                                                                   read_preference=ReadPreference.SECONDARY_PREFERRED)

            is_not_alived_c = get_db()["noc.cache.object_status"].find(
                {"object": {"$in": is_managed_undef_in},
                 "status": False},
                {"_id": 1, "object": 1},
                read_preference=ReadPreference.SECONDARY_PREFERRED).count()

            is_managed_alive_in = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-%d" %
                                   m["object"] for m in is_alive_id]
            is_managed_ng_in = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-%d" %
                                m_id for m_id in is_managed_not_generic_in]

            is_managed_g_in = ["discovery-noc.services.discovery.jobs.box.job.BoxDiscoveryJob-%d" %
                               m_id for m_id in is_managed_undef_in]

            bad_snmp_cred = get_db()["noc.joblog"].find({"problems.suggest_snmp": "Failed to guess SNMP community",
                                                         "_id": {"$in": is_managed_alive_in}},
                                                        read_preference=ReadPreference.SECONDARY_PREFERRED).count()
            bad_cli_cred = get_db()["noc.joblog"].find({"problems.suggest_cli": "Failed to guess CLI credentials",
                                                        "_id": {"$in": is_managed_ng_in}},
                                                       read_preference=ReadPreference.SECONDARY_PREFERRED).count()
            profile_not_found = get_db()["noc.joblog"].find({
                "problems.profile": {"$regex": "^Not find profile for OID:.*"},
                "_id": {"$in": is_managed_g_in}},
                read_preference=ReadPreference.SECONDARY_PREFERRED).count()

            # profile_not_detect = get_db()["noc.joblog"].find({
            #    "problems.profile": {"$regex": "^Cannot find profile in.*"},
            #    "_id": {"$in": is_managed_g_in}},
            #    read_preference=ReadPreference.SECONDARY_PREFERRED)

            # not_procc_yet = get_db()["noc.schedules.discovery." + p.name].find({"ls": {"$exists": False},
            #
            bad_snmp_cred_id = [r["_id"] for r in get_db()["noc.joblog"].find({
                "problems.suggest_snmp": "Failed to guess SNMP community",
                "_id": {"$in": is_managed_alive_in}},
                read_preference=ReadPreference.SECONDARY_PREFERRED)]
            profile_not_detect_id = [r["_id"] for r in get_db()["noc.joblog"].find({
                "problems.profile": {"$regex": "^Cannot find profile in.*"},
                "_id": {"$in": is_managed_g_in}},
                read_preference=ReadPreference.SECONDARY_PREFERRED)]
            not_procc_yet = 0
            # MO ID in variable reason
            var_ids = set([int(r.rsplit("-", 1)[1]) for r in set(is_managed_alive_in) - set(bad_snmp_cred_id)])
            # MO with disabled Box Discovery (@todo Or Profile Discovery)
            var1 = var_ids.intersection(set(is_box_dis.values_list("id", flat=True)))
            # Profile check false if credential is bad (no snmp)
            var2 = set([int(r.rsplit("-", 1)[1]) for r in profile_not_detect_id])
            # Other
            var3 = var_ids - var1
            var3 -= var2
            if is_managed_not_generic_c != 0:
                percent = (is_managed_not_generic_c / float(is_managed_c)) * 100
            else:
                percent = 100

            calc = [
                {"name": _("Not Managed"), "value": is_not_man.count() + is_not_resp.count()},
                {"name": _("Is Managed"), "value": is_managed_c},
                {"name": _("Is Managed, object type defined"), "value": is_managed_not_generic_c, "percent":
                    "%.2f %%" % percent},
                {"name": _("Is Managed, object type defined bad CLI Credential"), "value": bad_cli_cred},
                {"name": _("Is Managed, object type undefined"), "value": len(is_managed_undef_in)},
                {"name": _("Is Managed, object type undefined not ping response"), "value": is_not_alived_c},
                {"name": _("Is Managed, object type undefined has ping response"), "value": is_alive_id.count()},
                {"name": _("Is Managed, object type undefined bad SNMP Credential"), "value": bad_snmp_cred},
                {"name": _("Is Managed, object type undefined for various reasons"), "value":
                    is_alive_id.count() - bad_snmp_cred},
                {"name": _("Is Managed, object type Profile is not know"), "value": profile_not_found},
                {"name": _("Is Managed, object type Profile is not know that no SNMP"), "value": len(var2)},
                {"name": _("Is Managed, But Box discovery is disables"), "value": len(var1)},
                {"name": _("Is Managed, objects not processed yet"), "value": not_procc_yet},
            ]

            summary = [sum(e) for e in zip(summary, [i["value"] for i in calc])]
            # ALPHABET = {i[1]: i[0] for i in enumerate(u"npabcdefghijklmoqrstuvwxyz")}
            # calc[2]["value"] = "%d (%d%%)" % (is_managed_not_generic.count(), percent)
            for c in calc:
                data += [[s1[calc.index(c)], c["name"], c["value"], c.get("percent", None)]]

        data += [SectionRow("Summary")]
        for c in summary:
            if summary.index(c) == 2:
                # data += [[s1[summary.index(c)], calc[summary.index(c)]
                # ["name"], "%d (%d%%)" % (c, (c / float(summary[1]))*100)]]
                data += [[s1[summary.index(c)],
                          calc[summary.index(c)]["name"],
                          c, "%.2f %%" % ((c / float(summary[1]))*100)]]
                continue
            data += [[s1[summary.index(c)], calc[summary.index(c)]["name"], c, None]]

        return self.from_dataset(
            title=self.title,
            columns=[
                _("PP"),
                _("Status"),
                _("Quantity"),
                _("Percent")
            ],
            data=data
        )
