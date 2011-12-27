# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MRT Result Formatter
##----------------------------------------------------------------------
## INTERFACE: IReduceTask
##----------------------------------------------------------------------
## DESCRIPTION:
## Returns MRT Result
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

@pyrule
def mrt_result(task):
    """
    Format MRT task result to return as JSON
    :param task:
    :type task: ReduceTask
    :rtype: list
    """
    return [{
        "object_id": str(mt.managed_object.id),
        "object_name": mt.managed_object.name,
        "status": mt.status == "C",
        "script": mt.map_script,
        "result": mt.script_result
    } for mt in task.maptask_set.all()]
