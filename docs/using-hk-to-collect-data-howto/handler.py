# Python modules
import re

# NOC modules
from noc.core.mx import send_message, MX_LABELS, MX_H_VALUE_SPLITTER
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.subinterface import SubInterface
from noc.core.comp import DEFAULT_ENCODING

MGMT_VLAN_CAPS = "Management | VlanID"
IPv4 = "IPv4"


def handler_mgmt_vlan(object: ManagedObect) -> None:
    """
    Scan for an device management IP through the subinterfaces.
    If the sub is found look for `vlan_id` field. The VLAN found
    is considered as management vlan and stored in the
    `Management | VlanID` capability.
    """
    re_addr = re.compile(f"{object.address}.+")
    msub = SubInterface.objects.filter(
        ipv4_addresses=re_addr, managed_object=object, enabled_afi=IPv4, vlan_ids__exists=True
    ).first()
    if not msub or not msub.vlan_ids:
        return
    mgmt = object.get_caps(MGMT_VLAN_CAPS)
    if mgmt == msub.vlan_ids[0]:
        return
    object.set_caps(MGMT_VLAN_CAPS, msub.vlan_ids[0], source="manual")


def handler_vlans_script(object: ManagedObject) -> None:
    """
    Execute `get_vlans` script and sent the result as the message.
    """
    r = object.scripts.get_vlans()
    if not r:
        return
    # Add the label to use in condition
    labels = ["custom_data"] + object.effective_labels
    send_message(
        r,
        message_type="event",
        headers={
            MX_LABELS: MX_H_VALUE_SPLITTER.join(labels).encode(encoding=DEFAULT_ENCODING),
        },
    )


def hk_handler(job):
    """
    Housekeeper Entrypoint
    """
    mo: "ManagedObject" = job.object
    handler_mgmt_vlan(mo)
    handler_vlans_script(mo)
