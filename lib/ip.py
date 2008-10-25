##
## IP address manipulation routines
##
import struct,socket
##
##
##
def address_to_int(ip):
    return struct.unpack("L",socket.inet_aton(ip))[0]
##
##
##
def int_to_address(i):
    return socket.inet_ntoa(struct.pack("L",i))
##
## Converts bits to an integer
##
def bits_to_int(bits):
    return ((1L<<bits)-1L)<<(32L-bits)
##
## Converts bits to netmask
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
##
## Returns amount of addresses into prefix of "bits" length
##
def bits_to_size(bits):
    return 1L<<(32L-bits)
##
##
##
def network(prefix):
    n,m=prefix.split("/")
    m=int(m)
    return int_to_address(address_to_int(n)&bits_to_int(m))
##
##
##
def broadcast(prefix):
    n,m=prefix.split("/")
    m=int(m)
    return int_to_address(address_to_int(n)|(0xFFFFFFFFL^bits_to_int(m)))

##
## Returns a list of free block in "prefix"
## Allocated should be sorted list
##
def free_blocks(prefix,allocated):
    def boundary(p):
        n,m=p.split("/")
        m=int(m)
        a=address_to_int(n)
        b=bits_to_int(m)
        return (a&b,a|(0xFFFFFFFFL^b))
    def cover_blocks(f,t,b=[]):
        def rank(i):
            j=32
            n=1
            while (i&n)==0:
                j-=1
                n=(n<<1)|1
            return j
        n=rank(f)
        while True:
            size=bits_to_size(n)
            if t-f==size-1:
                return b+[int_to_address(f)+"/%d"%n]
            elif n==32 or t-f>size-1:
                return cover_blocks(f+size,t,b+[int_to_address(f)+"/%d"%n])
            n+=1
            
    used=[]
    p0,p1=boundary(prefix)
    for a in allocated:
        a0,a1=boundary(a)
        if a0<p0 or a1>p1:
            continue
        if used and a0-used[-1]==1:
            # Merge adjanced allocations
            used[-1]=a1
        else:
            used+=[a0,a1]
    free=[]
    while used:
        u0=used.pop(0)
        u1=used.pop(0)
        free+=[u0-1,u1+1]
    if p0<free[0]:
        free.insert(0,p0)
    else:
        free.pop(0)
    if p1>free[-1]:
        free+=[p1]
    else:
        free.pop(-1)
    r=[]
    while free:
        f=free.pop(0)
        t=free.pop(0)
        r+=cover_blocks(f,t)
    return r