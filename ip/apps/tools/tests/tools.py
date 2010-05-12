# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Test tools
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ApplicationTestCase
from noc.ip.models import *
import csv,cStringIO

class ToolsTestCase(ApplicationTestCase):
    fixtures=["tools.json"]
    ##
    ## Test index page available
    ##
    def test_index(self):
        # Get tools page
        index_page=self.app.get(self.base_url+"2/192.168.0.0/24/",user=self.user)
    ##
    ## Test download ip form
    ##
    def test_downloads(self,vrf_id=2):
        # Click "Download button"
        index_page=self.app.get(self.base_url+"%d/192.168.0.0/24/"%vrf_id,user=self.user)
        download=index_page.forms["download_ip"].submit()
        # Check content type
        self.assertEquals(download.content_type,"text/csv")
        # Check resulting CSV
        f=cStringIO.StringIO(download.body)
        addresses=set(["192.168.0.1","192.168.0.2","192.168.0.3"])
        reader=csv.reader(f)
        for row in reader:
            self.assertEquals(len(row),4)
            address,fqdn,description,tt=row
            self.assertIn(address,addresses)
            addresses.remove(address)
        # Check all addresses returned in CSV
        self.assertEquals(len(addresses),0)
    ##
    ## Test upload ip form
    ##
    def test_uploads(self):
        index_page=self.app.get(self.base_url+"2/192.168.0.0/24/",user=self.user)
        # Get data from VRF2
        download=index_page.forms["download_ip"].submit()
        data=download.body
        # Upload to VRF3
        index_page=self.app.get(self.base_url+"3/192.168.0.0/24/",user=self.user)
        action=index_page.forms["upload_ip"].action
        result=self.app.post(action,params={},user=self.user,upload_files=[("file","file.csv",data)])
        result=result.follow() # Follow redirect
        # Check upload result
        self.test_downloads(vrf_id=3)
