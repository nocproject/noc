# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SVG utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import urllib
##
## Idiotic implementation for font metrics
##
PADDING=2
CHAR_HEIGTH=10
CHAR_WIDTH=10

##
## Check wrether browser has SVG support
##
def has_svg_support(request):
    #ua=request.META.get("HTTP_USER_AGENT","")
    return True # Stub
##
## Returns rotated text width and height
##
def vertical_text_size(text):
    return (CHAR_HEIGTH+2*PADDING,len(text)*CHAR_WIDTH+2*PADDING)
##
## Returns SVG containing rotated text string
##
def vertical_text_svg(text):
    width,height=vertical_text_size(text)
    return u"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="%(width)d" height="%(height)d" viewBox="0 0 %(width)d %(height)d" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:space="preserve" version="1.1"  baseProfile="full">
    <defs>
        <style type="text/css">
        <![CDATA[
        .t {font-size:12px; font-family:"Lucida Grande","DejaVu Sans","Bitstream Vera Sans",Verdana,Arial,sans-serif; color:#333;}
        ]]>
        </style>
    </defs>
    <text class="t" x="%(cx)d" y="%(cy)d" transform="rotate(-90 %(cx)d %(cy)d)">%(text)s</text>
</svg>"""%{
        "width" : width,
        "height": height,
        "cx"    : CHAR_HEIGTH+PADDING,
        "cy"    : height-PADDING,
        "text"  : text
        }
##
## Returns embed tag for rotated text
##
def vertical_text_inline(text):
    width,height=vertical_text_size(text)
    text=urllib.quote(text)
    return "<embed width='%d' height='%d' src='/main/svg/text/vertical/?text=%s' type='image/svg+xml'>"%(width,height,text)
