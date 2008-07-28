#
# RPLS manipulation utilities
#

# rpsl_format(rpsl)
# idents RPSL by aligning left side of values
# Emply strings and strings without ':' are silently dropped
#
RPLS_IDENT=20
def rpsl_format(rpsl,ident=None):
    if ident is None:
        ident=RPLS_IDENT
    out=[]
    mask="%%-%ds%%s"%ident
    for l in [x for x in rpsl.split("\n") if ":" in x]:
        k,v=l.split(":",1)
        out.append(mask%(k.strip()+":",v.strip()))
    return "\n".join(out)
