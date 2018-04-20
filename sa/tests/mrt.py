# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Map/Reduce Tasks unittests
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.test import NOCTestCase
from noc.sa.models import ReduceTask

class MRTTestCase(NOCTestCase):
    def test_sae_task_single(self):
        task = ReduceTask.create_task("SAE", None, {}, "ping_test",
                {"activator_name": "default", "addresses": ["127.0.0.1"]}, 1)
        self.assertEquals(task.maptask_set.count(), 1)
        mt = task.maptask_set.all()[0]
        self.assertEquals(mt.map_script, "NOC.SAE.ping_test")

    def test_sae_task_multiple(self):
        task = ReduceTask.create_task("SAE", None, {}, ["ping_test"] * 2,
            [{"activator_name": "default", "addresses": ["127.0.0.1"]}] * 2, 1)
        self.assertEquals(task.maptask_set.count(), 2)

    def test_sae_task_multiple2(self):
            task = ReduceTask.create_task(["SAE", "SAE"], None, {},
                ["ping_test"] * 2,
                [{"activator_name": "default", "addresses": ["127.0.0.1"]}] * 2, 1)
            self.assertEquals(task.maptask_set.count(), 4)
