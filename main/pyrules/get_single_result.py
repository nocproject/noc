# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## get_single_result reduce task
##----------------------------------------------------------------------
## INTERFACE: IReduceTask
##----------------------------------------------------------------------
## DESCRIPTION:
## Returns result of single map task, or None in case of failure
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
@pyrule
def get_single_result(task):
    mt=task.maptask_set.all()[0]
    if mt.status!="C":
        return None
    return mt.script_result
