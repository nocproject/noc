# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Activator Status Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport,TableColumn
from noc.settings import config
import socket
from xmlrpclib import ServerProxy, Error
##
##
##
class Reportreportactivatorstatus(SimpleReport):
    title="Activator Status"
    def get_data(self,**kwargs):
        server=ServerProxy("http://%s:%d"%(config.get("xmlrpc","server"),config.getint("xmlrpc","port")))
        try:
            data=server.activator_status()
        except socket.error,why:
            data=[]
        return self.from_dataset(title=self.title,
            columns=["Activator",TableColumn("Status",format="bool")],
            data=data)
