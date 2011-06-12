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
from noc.sa.interfaces import IGetInterfaceStatus, MACAddressParameter
import re
##
## @todo: ["mac"] support by SNMP
##

rx_interface_status=re.compile(r"^(?P<interface>.+?)\s+is\s+\S+,\s+line\s+protocol\s+is\s+(?P<status>up|down).*?index is (?P<ifindex>\d+).*?address is (?P<mac>\S+).*?",re.IGNORECASE|re.DOTALL)
rx_interface_descr=re.compile(r".*?alias name is (?P<descr>[^,]+?),.*?",re.IGNORECASE|re.DOTALL)
rx_interface_status_3526=re.compile(r"Information of (?P<interface>[^\n]+?)\n.*?Mac Address:\s+(?P<mac>[^\n]+?)\n(?P<block>.*)",re.MULTILINE|re.IGNORECASE|re.DOTALL)
rx_interface_intstatus_3526=re.compile(r".*?Name:[^\n]* (?P<descr>[^\n]*?)\n.*?Link Status:\s+(?P<intstatus>up|down)\n",re.MULTILINE|re.IGNORECASE|re.DOTALL)
rx_interface_linestatus_3526=re.compile(r"Port Operation Status:\s+(?P<linestatus>up|down)\n",re.MULTILINE|re.IGNORECASE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="EdgeCore.ES.get_interface_status"
    implements=[IGetInterfaceStatus]
    cache=True

    def execute(self,interface=None):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Get interface status
                r=[]
                for i,n,s,d,m in self.join_four_tables(self.snmp,"1.3.6.1.2.1.31.1.1.1.1","1.3.6.1.2.1.2.2.1.8","1.3.6.1.2.1.31.1.1.1.18","1.3.6.1.2.1.2.2.1.6",bulk=True,cached=True): # IF-MIB::ifName, IF-MIB::ifOperStatus, IF-MIB::ifAlias, IF-MIB::ifPhysAddress
		    if not n.startswith("Port-Channel"):
			n=n.replace("Port","Eth 1/")
			if n=="":
			    continue
                    r+=[{"snmp_ifindex":i,"interface":n,"status":int(s)==1,"description":d,"mac":m}] # ifOperStatus up(1)
                return r
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        r=[]
	s=[]
	if self.match_version(platform__contains="4626"):
	    try:
    		cmd="show interface status | include line protocol is|alias|address is"
		buf=self.cli(cmd,cached=True).replace("\n "," ")
	    except:
    		cmd="show interface status"
		buf=self.cli(cmd,cached=True).replace("\n "," ")
    	    for l in buf.splitlines():
        	match=rx_interface_status.match(l)
        	if match:
            	    r+=[{
                	"interface"    : match.group("interface"),
                	"status"       : match.group("status")=="up",
			"mac"          : MACAddressParameter().clean(match.group("mac")),
			"snmp_ifindex" : match.group("ifindex")
                    }]
		    mdescr=rx_interface_descr.match(l)
		    if mdescr:
			r[-1]["description"]=mdescr.group("descr")
	else:
    	    cmd="show interface status"
	    buf=self.cli(cmd,cached=True).lstrip("\n\n")
	    for l in buf.split("\n\n"):
		match=rx_interface_status_3526.search(l+"\n")
		if match:
		    descr=""
		    interface=match.group("interface").replace("VLAN ","VLAN")
		    if interface.startswith("VLAN"):
			intstatus="up"
			linestatus="up"
		    else:
			if match.group("block"):
			    block=match.group("block")
			    submatch=rx_interface_intstatus_3526.search(block)
			    if submatch:
				descr=submatch.group("descr")
				intstatus=submatch.group("intstatus").lower()
			    linestatus="down"
			    submatch=rx_interface_linestatus_3526.search(block)
			    if submatch:
				linestatus=submatch.group("linestatus").lower()
            	    r+=[{
                	"interface"    : interface,
			"mac"          : MACAddressParameter().clean(match.group("mac")),
                	"status"       : linestatus=="up",
                    }]
		    if descr:
			r[-1]["description"]=descr

        return r

    ##
    ## Generator returning a rows of 4 snmp tables joined by index
    ##
    def join_four_tables(self,snmp,oid1,oid2,oid3,oid4,community_suffix=None,bulk=False,min_index=None,max_index=None,cached=False):
        t1=snmp.get_table(oid1,community_suffix=community_suffix,bulk=bulk,min_index=min_index,max_index=max_index,cached=cached)
        t2=snmp.get_table(oid2,community_suffix=community_suffix,bulk=bulk,min_index=min_index,max_index=max_index,cached=cached)
	t3=snmp.get_table(oid3,community_suffix=community_suffix,bulk=bulk,min_index=min_index,max_index=max_index,cached=cached)
	t4=snmp.get_table(oid4,community_suffix=community_suffix,bulk=bulk,min_index=min_index,max_index=max_index,cached=cached)
        for k1,v1 in t1.items():
            try:
                yield (k1,v1,t2[k1],t3[k1],t4[k1])
            except KeyError:
                pass
