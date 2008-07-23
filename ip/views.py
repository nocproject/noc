from django.shortcuts import get_object_or_404
from noc.ip.models import VRFGroup,VRF,IPv4BlockAccess
from noc.lib.render import render
from noc.lib.validators import is_rd

def index(request):
    search_by_name=None
    search_by_rd=None
    query=None
    if request.POST:
        if request.POST["search"]:
            query=request.POST["search"]
            if is_rd(query):
                search_by_rd=query
            else:
                search_by_name=query
    l=[]
    for vg in VRFGroup.objects.all():
        if search_by_name:
            vrfs=vg.vrf_set.filter(name__icontains=search_by_name)
        elif search_by_rd:
            vrfs=vg.vrf_set.filter(rd__exact=search_by_rd)
        else:
            vrfs=vg.vrf_set.all()
        if len(vrfs)>0:
            l.append((vg,vrfs.order_by("name")))
    if query is None:
        query=""
    return render(request,"ip/index.html",{"groups":l,"query":query})
    
def vrf_index(request,vrf_id,prefix="0.0.0.0/0"):
    vrf_id=int(vrf_id)
    vrf=get_object_or_404(VRF,id=vrf_id)
    parents=vrf.prefix(prefix).parents
    prefixes=vrf.prefixes(prefix)
    can_allocate=IPv4BlockAccess.check_write_access(request.user,vrf,prefix)
    prefix=vrf.prefix(prefix)
    return render(request,"ip/vrf_index.html",{"vrf":vrf,"parents":parents,"prefixes":prefixes,"prefix":prefix,
                        "can_allocate":can_allocate})