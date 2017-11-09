# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.SwOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces

class Script(BaseScript):
    name = "MikroTik.SwOS.get_interfaces"
    interface = IGetInterfaces

    def execute(self):
        interfaces = []

        if self.has_snmp():
            try:
                for i,d in self.snmp.join_tables(
                					"1.3.6.1.2.1.2.2.1.1", 
                					"1.3.6.1.2.1.2.2.1.2"):

                	if self.snmp.get("1.3.6.1.2.1.2.2.1.7.%d" % i) == 1:
                		admin_status = True
                	else:
                		admin_status = False

                	if self.snmp.get("1.3.6.1.2.1.2.2.1.8.%d" % i) == 1:
                		oper_status = True
                	else:
                		oper_status = False

			interfaces += [{
		    	    "name": d,
		            "snmp_ifindex": i,
		            "type": "physical",
		            "mac": self.snmp.get("1.3.6.1.2.1.2.2.1.6.%d" % i),
		            "admin_status": admin_status,
		            "oper_status": oper_status,
		            "subinterfaces": [{
		                "name": d,
		                "admin_status": admin_status,
		                "oper_status": oper_status,
		                "enabled_afi": ["BRIDGE"]
		            }]
			}]
		return [{"interfaces": interfaces}]

            except self.snmp.TimeOutError:
                pass
