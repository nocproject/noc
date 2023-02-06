# ---------------------------------------------------------------------
# Update segment redundancy
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from noc.sa.models.administrativedomain import AdministrativeDomain
from noc.inv.models.networksegment import NetworkSegment
from noc.inv.models.object import Object


def fix():
    for mo_id, adm_id, seg_id, cont_id in ManagedObject.objects.filter(adm_path=[]).values_list(
        "id", "administrative_domain", "segment", "container"
    ):
        ns = NetworkSegment.get_by_id(seg_id)
        ad = AdministrativeDomain.get_by_id(adm_id)
        adm_path = ad.get_path()
        segment_path = [str(sid) for sid in ns.get_path()]
        container_path = []
        if cont_id:
            container = Object.get_by_id(cont_id)
            container_path = [str(sid) for sid in container.get_path()] if container else []
        ManagedObject.objects.filter(id=mo_id).update(
            adm_path=adm_path,
            segment_path=segment_path,
            container_path=container_path,
        )
        ManagedObject._reset_caches(mo_id)


from noc.inv.models.networksegmentprofile import NetworkSegmentProfile

ns_profile = NetworkSegmentProfile.objects.get(name="rf_agg")
base_segment = NetworkSegment.objects.get(name="Новые: Екатеринбургский филиал")

for mo in ManagedObject.objects.filter(object_profile__name="sw.agg"):
    ns_name = t.render_body(**{"attacker": mo})
    print(f"[{mo.name}] Segment: {ns_name}")
    ns = NetworkSegment.objects.filter(name=ns_name).first()
    if not ns:
        ns = NetworkSegment(name=ns_name, parent=base_segment, profile=ns_profile)
        ns.save()
    if not mo.container:
        mo.segment = ns
        mo.save()
        continue
    for mo in ManagedObject.objects.filter(container=mo.container):
        if mo.segment != ns:
            mo.segment = ns
            mo.save()
