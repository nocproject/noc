# ----------------------------------------------------------------------
# VLAN tag manipulation engine
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


def process_vlan_map(vlans, rules):
    """
    Apply VLAN translation rules for ethernet services.
    `vlans` are coded by list:
    * [] - untagged packet
    * [inner vlan] - 802.1Q
    * [outer vlan, inner vlan] - Q-in-Q
    By convention top of stack is first element.

    In additional to input vlan stack, internal vlan stack maintained.
    Internal stack populated by *pop* operations and
    can be popped by *push* and *swap* operations when *vlan* parameter is empty.

    Rules coded as dicts each with keys:
    * op - operation. One of:
      * pop -- Pop first tag and push to internal stack
      * push -- Push *vlan* parameter into vlan stack.
                If *vlan* parameter is empty - pop it from internal stack
      * swap - If *vlan* is not empty - push atop internal stack.
               Swap tops of vlan stack and of internal stack
      * drop - Drop top of internal stack
    * vlan - optional VLAN parameter

    :param vlans: List of input vlan tags.
    :param rules: List of rules
    :return: List of output vlan tags
    """
    result = vlans[:]
    stack = []
    for rule in rules:
        op = rule.get("op")
        if op == "pop":
            stack.insert(0, result.pop(0))
        elif op == "push":
            vlan = rule.get("vlan")
            if vlan is None:
                vlan = stack.pop(0)
            result.insert(0, vlan)
        elif op == "swap":
            vlan = rule.get("vlan")
            if vlan is None:
                vlan = stack.pop(0)
            v = result.pop(0)
            result.insert(0, vlan)
            stack.insert(0, v)
        elif op == "drop":
            stack.pop(0)
        elif op is None:
            raise ValueError("Missed operation")
        else:
            raise ValueError("Invalid operation: %s" % op)
    return result


def process_chain(vlans, chain):
    """
    Pass vlan stack through the chain of rules
    :param vlans: Vlan stack as in process_vlan_map function
    :param chain: List of list of rules. i.e.  [first ingress, first egress, ..., last ingress, last egress]
    :return: Vlan stack as in process_vlan_map function
    """
    result = vlans[:]
    for rules in chain:
        result = process_vlan_map(result, rules)
    return result
