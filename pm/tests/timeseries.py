# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## TimeSeries models test
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.test import ModelTestCase
from noc.pm.models import *
##
##
##
class TimeSeriesTestCase(ModelTestCase):
    model=TimeSeries
    ##
    ##
    ##
    def get_data(self):
        for i in range(10):
            yield {"name":"name%d"%i,"is_enabled":i%2!=0}
    ##
    ## Test TimeSeries.register method
    ##
    def test_register(self):
        # Tegister sample data
        tsdata=[("ts1",1273032709,1.0),("ts2",1273032710,2.5),("ts1",1273032769,2.0),("ts2",1273032770,2.0)]
        tsnames=set()
        for ts,timestamp,v in tsdata:
            tsnames.add(ts)
            TimeSeries.register(ts,timestamp,v)
        # Test all timeseries created
        for ts in tsnames:
            TimeSeries.objects.get(name=ts)
