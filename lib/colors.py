# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Color scheme generator
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import math
##
## HSV -> RGB convertor, for Python 2.5 compatibility
##
def hsv_to_rgb(h,s,v):
    h=float(h)
    hi=math.floor(h/60.0)%6
    f=(h/60.0)-math.floor(h/60.0)
    p=v*(1.0-s)
    q=v*(1.0-(f*s))
    t=v*(1.0-((1.0-f)*s))
    return {
        0: (v, t, p),
        1: (q, v, p),
        2: (p, v, t),
        3: (p, q, v),
        4: (t, p, v),
        5: (v, p, q),
    }[hi]

##
## Generate N contrast colors
##
def get_colors(N):
    """
    >>> list(get_colors(1))
    ['#ff0000']
    >>> list(get_colors(2))
    ['#ff0000', '#00ffff']
    >>> list(get_colors(3))
    ['#00ff00', '#ff0000', '#0000ff']
    >>> list(get_colors(4))
    ['#ff0000', '#00ffff', '#7fff00', '#7f00ff']
    """
    MP=12       # Maximum points on color circle
    p=min(N,MP) # Points on color circle
    d=360//p    # Step on color circle
    V=255 # Value
    S=1   # Saturation
    hs=[]
    while N:
        if not hs:
            # Rebuild colors
            hs=[i*d for i in range(p)]
        H=hs.pop(len(hs)/2 if N%2 else 0)
        # Yield current color
        yield "#%02x%02x%02x"%(hsv_to_rgb(H,S,V))
        N=N-1
        if not hs:
            # Reduce value for next round
            V=V*3//4
    

