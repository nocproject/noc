# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SNMP Get probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.nbsocket import UDPSocket
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api
from noc.pm.probes import *
import re

##
## SNMP Probe
##
class SNMPSocket(UDPSocket):
    def __init__(self,probe,service,oids,community):
        self.probe=probe
        self.service=service
        super(SNMPSocket,self).__init__(self.probe.factory)
        self.oids=oids
        self.community=community
        self.req_PDU=None
        self.sendto(self.get_snmp_request(),(self.service,161))
    ##
    ## Convert oid from string to a list of integers
    ##
    def oid_to_tuple(self,oid):
        return [int(x) for x in oid.split(".")]
    ##
    ## Returns string containing SNMP GET requests to self.oids
    ##
    def get_snmp_request(self):
        self.probe.debug("%s SNMP GET %s"%(self.service,str(self.oids)))
        p_mod=api.protoModules[api.protoVersion2c]
        req_PDU =  p_mod.GetRequestPDU()
        p_mod.apiPDU.setDefaults(req_PDU)
        p_mod.apiPDU.setVarBinds(req_PDU,[(self.oid_to_tuple(oid),p_mod.Null()) for oid in self.oids])
        req_msg = p_mod.Message()
        p_mod.apiMessage.setDefaults(req_msg)
        p_mod.apiMessage.setCommunity(req_msg, self.community)
        p_mod.apiMessage.setPDU(req_msg, req_PDU)
        self.req_PDU=req_PDU
        return encoder.encode(req_msg)
    ##
    ## Read and parse reply.
    ## Call set_data for all returned values
    ##
    def on_read(self,data,address,port):
        p_mod=api.protoModules[api.protoVersion2c]
        while data:
            rsp_msg, data = decoder.decode(data, asn1Spec=p_mod.Message())
            rsp_pdu = p_mod.apiMessage.getPDU(rsp_msg)
            if p_mod.apiPDU.getRequestID(self.req_PDU)==p_mod.apiPDU.getRequestID(rsp_pdu):
                errorStatus = p_mod.apiPDU.getErrorStatus(rsp_pdu)
                if errorStatus:
                    self.probe.error("%s SNMP GET ERROR: %s"%(self.service,errorStatus.prettyPrint()))
                else:
                    for oid, val in p_mod.apiPDU.getVarBinds(rsp_pdu):
                        self.probe.debug('%s SNMP GET REPLY: %s %s'%(self.service,oid.prettyPrint(),val.prettyPrint()))
                        self.set_data(oid.prettyPrint(),val.prettyPrint())
        self.close()
    ##
    ## Convert value to float and set to probe
    ##
    def set_data(self,param,value):
        self.probe.set_data(self.service,param,float(value) if value!="" and value!="''" and value is not None else None)
    ##
    ## Set result
    ##
    def set_result(self,result,message="OK"):
        self.probe.set_result(self.service,result,message)
    ##
    ## Unregister socket
    ##
    def on_close(self):
        self.probe.on_close(self.service)
##
## IfIndex table resolver
##
class SNMPIfIndexSocket(SNMPSocket):
    TTL=60
    def __init__(self,probe,service,interfaces,community):
        self.oid_root="1.3.6.1.2.1.2.2.1.2"
        self.interfaces=set(interfaces)
        self.ifindex=[]
        super(SNMPIfIndexSocket,self).__init__(probe,service,[],community)
    ##
    ## Fill GET NEXT Request
    ##
    def get_snmp_request(self):
        self.probe.debug("%s SNMP GETNEXT %s"%(self.service,str(self.oid_root)))
        p_mod=api.protoModules[api.protoVersion2c]
        req_PDU =  p_mod.GetNextRequestPDU()
        p_mod.apiPDU.setDefaults(req_PDU)
        p_mod.apiPDU.setVarBinds(req_PDU,[(p_mod.ObjectIdentifier(self.oid_to_tuple(self.oid_root)),p_mod.Null())])
        req_msg = p_mod.Message()
        p_mod.apiMessage.setDefaults(req_msg)
        p_mod.apiMessage.setCommunity(req_msg, self.community)
        p_mod.apiMessage.setPDU(req_msg, req_PDU)
        self.req_PDU=req_PDU
        self.req_msg=req_msg
        return encoder.encode(req_msg)
    ##
    ## Read the table and populate self.ifindex
    ##
    def on_read(self,data,address,port):
        p_mod=api.protoModules[api.protoVersion2c]
        while data:
            rsp_msg, data = decoder.decode(data, asn1Spec=p_mod.Message())
            rsp_pdu = p_mod.apiMessage.getPDU(rsp_msg)
            # Match response to request
            if p_mod.apiPDU.getRequestID(self.req_PDU)==p_mod.apiPDU.getRequestID(rsp_pdu):
                # Check for SNMP errors reported
                errorStatus = p_mod.apiPDU.getErrorStatus(rsp_pdu)
                if errorStatus and errorStatus != 2:
                    raise errorStatus
                # Format var-binds table
                var_bind_table = p_mod.apiPDU.getVarBindTable(self.req_PDU, rsp_pdu)
                # Report SNMP table
                for table_row in var_bind_table:
                    for name, val in table_row:
                        if val is None:
                            continue
                        oid=name.prettyPrint()
                        if not oid.startswith(self.oid_root):
                            self.close()
                            return
                        ifname=str(val)
                        ifindex=oid.split(".")[-1]
                        if ifname in self.interfaces:
                            self.interfaces.remove(ifname)
                            self.ifindex+=[(ifindex,ifname)]
                if not self.interfaces:
                    # All intefaces are resolved
                    self.close()
                    return
                # Stop on EOM
                for oid, val in var_bind_table[-1]:
                    if val is not None:
                        break
                    else:
                        self.close()
                        return
                # Generate request for next row
                p_mod.apiPDU.setVarBinds(self.req_PDU, map(lambda (x,y),n=p_mod.Null(): (x,n), var_bind_table[-1]))
                p_mod.apiPDU.setRequestID(self.req_PDU, p_mod.getNextRequestID())
                self.sendto(encoder.encode(self.req_msg),(self.service,161))
        return
    ##
    ## Return ifindexes to the probe
    ##
    def on_close(self):
        if self.interfaces:
            # There are still unresolved interfaces
            self.probe.error("Unable to resolve interfaces: %s"%", ".join(self.interfaces))
        self.probe.set_ifindex(self.service,self.ifindex)
##
## Configuration options
## community =
## oid.<name> = <oid>
## type.<name> = counter|gauge
## scale.<name> = scale
## optional:
## Interfaces =
##
class SNMPProbe(Probe):
    name="snmp" # Abstract probe
    socket_class=SNMPSocket
    def __init__(self,daemon,probe_name,config):
        self.sockets={} # Service -> socket
        self.oids={}    # service -> oid -> name
        self.ifindex={} # service -> ({ifindex->name},{name->ifindex})
        super(SNMPProbe,self).__init__(daemon,probe_name,config)
        self.interfaces=self.expand_config_list("interfaces")
        self.community=self.get("community")
        if self.interfaces:
            self.resolve_ifindexes()
        else:
            self.expand_parameters()
    
    def delay_parameter_expansion(self):
        return True
    
    def update_oids(self,service,oid,name):
        if not oid:
            return
        if service not in self.oids:
            self.oids[service]={oid:name}
        else:
            self.oids[service][oid]=name
    ##
    ## Expand parameter.
    ## Parameters with names containing {{ifindex}} will be expanded for each interface
    ##
    def expand_parameter(self,service,name,description):
        oid=description.get("oid")
        if "{{ifname}}" in name:
            for i in self.interfaces:
                nn=name.replace("{{ifname}}",i)
                n="%s.%s.%s"%(service,self.probe_name,nn)
                self.params[n]=Param(self,n,description)
                if oid:
                    self.update_oids(service,oid.replace("{{ifindex}}",self.ifindex[service][1][i]),nn)
        else:
            super(SNMPProbe,self).expand_parameter(service,name,description)
            self.update_oids(service,oid,name)
    ##
    ## In additional to superclass's expand_parametes()
    ##
    def expand_parameters(self):
        super(SNMPProbe,self).expand_parameters()
        # Read types
        types={}
        for opt in [opt for opt in self.config.options(self.probe_name) if opt.startswith("type.")]:
            types[opt[5:]]=self.get(opt)
        # Read scales
        scales={}
        for opt in [opt for opt in self.config.options(self.probe_name) if opt.startswith("scale.")]:
            scales[opt[6:]]=self.getfloat(opt)
        # Pupulate parameters from config file
        for opt in [opt for opt in self.config.options(self.probe_name) if opt.startswith("oid.")]:
            name=opt[4:]
            oid=self.get(opt)
            for s in self.services:
                d={"oid":oid}
                if name in types:
                    d["type"]=types[name]
                if name in scales:
                    d["scale"]=scales[name]
                self.expand_parameter(s,name,d)
    ##
    ## Set new ifindex mapping for service
    ##
    def set_ifindex(self,service,ifindex):
        self.debug("Setting ifindexes for %s: %s"%(service,str(ifindex)))
        if not ifindex:
            try:
                del self.ifindex[service]
            except:
                pass
            return
        ifindex_to_name={}
        name_to_ifindex={}
        for i,n in ifindex:
            ifindex_to_name[i]=n
            name_to_ifindex[n]=i
        self.ifindex[service]=(ifindex_to_name,name_to_ifindex)
        if not self.params:
            self.expand_parameters() # Expand parameters after IfIndex resolving
    ##
    ## Start ifindex resolving
    ##
    def resolve_ifindexes(self):
        for s in self.services:
            SNMPIfIndexSocket(self,s,self.interfaces,self.community)
    
    ##
    ## Start new check round
    ##
    def on_start(self):
        for service in self.services:
            if self.interfaces and service not in self.ifindex: # IfIndexes are not resolved yet
                continue
            self.sockets[service]=self.socket_class(self,service,self.oids[service].keys(),self.community)
        # Exit when not ifindexes resolved yet
        if len(self.sockets)==0:
            self.exit()
    ##
    ## Force remaining sockets closing
    ##
    def on_stop(self):
        for service,sock in self.sockets.items():
            sock.set_result(PR_FAIL,"Timeout expired")
            sock.close()
    ##
    ## Close probe if no sockets left
    ##
    def on_close(self,service):
        del self.sockets[service]
        if len(self.sockets)==0:
            self.exit()
    ##
    ## Resolve oids to symbolic name before saving
    ##
    def set_data(self,service,param,value):
        super(SNMPProbe,self).set_data(service,self.oids[service][param],value)
