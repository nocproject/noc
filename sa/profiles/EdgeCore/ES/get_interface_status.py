# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetInterfaceStatus
import re

#rx_interface_status=re.compile(r"^(?P<interface>\S+\s+\S+)\s+is\s+\S+,\s+line\s+protocol\s+is\s+(?P<status>up|down).*$",re.IGNORECASE)
rx_interface_status=re.compile(r"^(?P<interface>.+?)\s+is\s+\S+,\s+line\s+protocol\s+is\s+(?P<status>up|down).*$",re.IGNORECASE)
#rx_interface_status_3526=re.compile(r"Information of (?P<interface>[^\n]+)\n.+?Link Status:\s+(?P<status>up|down).*$",re.IGNORECASE)
rx_interface_status_3526=re.compile(r"Information of (?P<interface>[^\n]+)\n(?P<block>.*?)\n\n",re.MULTILINE|re.IGNORECASE|re.DOTALL)
rx_interface_intstatus_3526=re.compile(r"Link Status:\s+(?P<intstatus>up|down)\n",re.MULTILINE|re.IGNORECASE|re.DOTALL)
rx_interface_linestatus_3526=re.compile(r"Port Operation Status:\s+(?P<linestatus>up|down)\n",re.MULTILINE|re.IGNORECASE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="EdgeCore.ES.get_interface_status"
    implements=[IGetInterfaceStatus]
    def execute(self,interface=None):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Get interface status
                r=[]
                for n,s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1","1.3.6.1.2.1.2.2.1.8",bulk=True): # IF-MIB::ifName, IF-MIB::ifOperStatus
		    if not n.startswith("Port-Channel"):
			n=n.replace("Port","Eth 1/")
			if n=="":
			    continue
                    r+=[{"interface":n,"status":int(s)==1}] # ifOperStatus up(1)
                return r
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        r=[]
	s=[]
	try:
    	    cmd="show interface status | include line protocol is"
	    s=self.cli(cmd).splitlines()
	except self.CLISyntaxError:
    	    cmd="show interface status"
	    buf=self.cli(cmd)
	    for l in buf.splitlines():
        	match=rx_interface_status.match(l)
        	if match:
		    s+=[l]
	    if len(s)==0:
		for match in rx_interface_status_3526.finditer(buf):
		    interface=match.group("interface").replace("VLAN ","VLAN")
		    if interface.startswith("VLAN"):
			intstatus="up"
			linestatus="up"
		    else:
			block=match.group("block")
			submatch=rx_interface_intstatus_3526.search(block)
			if submatch:
			    intstatus=submatch.group("intstatus").lower()
			linestatus="down"
			submatch=rx_interface_linestatus_3526.search(block)
			if submatch:
			    linestatus=submatch.group("linestatus").lower()
		    s+=[interface+" is "+intstatus+", line protocol is "+linestatus]
        
        for l in s:
            match=rx_interface_status.match(l)
            if match:
                r+=[{
                    "interface" : match.group("interface"),
                    "status"    : match.group("status")=="up"
                    }]
        return r
