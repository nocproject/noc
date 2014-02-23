#!./bin/python
##----------------------------------------------------------------------
## Rebuild inter-pop links
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##---------------------------------------------------------------------

## NOC modules
from noc.inv.models.object import Object
from noc.inv.models.objectconnection import ObjectConnection
from noc.inv.models.link import Link

pop_map = {}  # object -> PoP
mo_pop = {}  # managed object id -> pop


def get_pop(o):
    """
    Find PoP of the object.
    Returns pop object or None
    """
    pop = pop_map.get(o)
    if pop:
        return pop
    if o.get_data("pop", "level"):
        # PoP itself
        pop_map[o] = o
        return o
    if not o.container:
        pop_map[o] = None
        return None
    else:
        parent = Object.objects.get(id=o.container)
        pop = get_pop(parent)
        pop_map[o] = pop
        return pop


def load_managed_objects():
    print "Load managed objects"
    for o in Object.objects.filter(data__management__managed_object__exists=True):
        mo_pop[o.get_data("management", "managed_object")] = get_pop(o)


def build_links():
    print "Building links"
    links = {}
    for l in Link.objects.all():
        mos = set()
        for i in l.interfaces:
            mos.add(i.managed_object.id)
        if len(mos) == 2:
            o1 = mos.pop()
            o2 = mos.pop()
            pop1 = mo_pop.get(o1)
            pop2 = mo_pop.get(o2)
            if pop1 and pop2 and pop1 != pop2:
                if pop1.id > pop2.id:
                    pop1, pop2 = pop2, pop1
                level = min(pop1.get_data("pop", "level"),
                            pop2.get_data("pop", "level")) // 10
                if (pop1, pop2) not in links:
                    links[pop1, pop2] = {
                        "level": level
                    }
    return links


def gen_db_links():
    print "Loading DB links"
    for oc in ObjectConnection.objects.filter(type="pop_link"):
        pops = [c.object for c in oc.connection]
        pop1, pop2 = pops
        if pop1.id > pop2.id:
            pop1, pop2 = pop2, pop1
        yield oc, pop1, pop2, {"level": oc.data["level"]}


def update_links():
    links = build_links()
    for oc, pop1, pop2, data in gen_db_links():
        level = data["level"]
        if (pop1, pop2) in links:
            if links[pop1, pop2]["level"] != level:
                level = links[pop1, pop2]["level"]
                print "Updating %s - %s level to %d" % (pop1, pop2, level)
                oc.data["level"] = level
                oc.save()
            del links[pop1, pop2]
        else:
            print "Unlinking %s - %s" % (pop1, pop2)
            oc.delete()
    # New links
    for pop1, pop2 in links:
        level = links[pop1, pop2]["level"]
        print "Linking %s - %s (level %d)" % (pop1, pop2, level)
        pop1.connect_genderless("links", pop2, "links",
                                {"level": level}, type="pop_link")


if __name__ == "__main__":
    load_managed_objects()
    update_links()
