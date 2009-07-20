# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Activator status
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column,BooleanColumn
import noc.main.report
from noc.settings import config
import socket
from xmlrpclib import ServerProxy, Error

class Report(noc.main.report.Report):
    name="sa.activator_status"
    title="Activator Status"
    requires_cursor=False
    columns=[Column("Activator"),BooleanColumn("Status")]
    
    def get_queryset(self):
        server=ServerProxy("http://%s:%d"%(config.get("xmlrpc","server"),config.getint("xmlrpc","port")))
        try:
            result=server.activator_status()
        except socket.error,why:
            result=[]
        return result
