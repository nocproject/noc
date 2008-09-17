##
## IP address manipulation routines
##
def bits_to_netmask(bits):
    try:
        bits=int(bits)
        if bits<=0 or bits>32:
            raise Exception
    except:
        return "255.255.255.255"
    m=((1L<<bits)-1L)<<(32L-bits)
    return ".".join(["%d"%(x&0xFF) for x in [m>>24,m>>16,m>>8,m]])