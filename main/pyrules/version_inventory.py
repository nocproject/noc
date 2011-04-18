# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## version_inventory reduce task
##----------------------------------------------------------------------
## INTERFACE: IReduceTask
##----------------------------------------------------------------------
## DESCRIPTION:
## Check version inventory completion status,
## update Managed Object's attributes and notify
## about changes
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
@pyrule
def version_inventory(task):
    from noc.main.models import SystemNotification
    
    changes = []
    for mt in task.maptask_set.filter(status="C"):
        mo = mt.managed_object
        c = [] # name, old, new
        for k,v in mt.script_result.items():
            if k == "attributes":
                for kk, vv in v.items():
                    ov = mo.get_attr(kk)
                    if ov != vv:
                        mo.set_attr(kk, vv)
                        c += [(kk, ov, vv)]
            else:
                ov = mo.get_attr(k)
                if ov != v:
                    mo.set_attr(k, v)
                    c += [(k, ov, v)]
        if c:
            changes += [mo.name+":"]
            for name, old, new in c:
                if old:
                    changes += ["    %s: %s -> %s" % (name, old, new)]
                else:
                    changes += ["    %s: %s (created)" % (name, new)]
            changes += []
    if changes:
        SystemNotification.notify(name="sa.version_inventory",
            subject="Version inventory changes", body="\n".join(changes))

