//---------------------------------------------------------------------
// Status workplace
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
Ext.define("NOC.main.desktop.StatusPanel", {
    extend: "Ext.Panel",
    id: "status",
    region: "south",
    height: 20,
    collapsible: true,
    animCollapse: true,
    collapseMode: "mini",
    split: true,
    preventHeader: true,
    layout: "hbox",
    items: [
        {
            xtype: "container",
            html: "&copy;2007-2011, <A HREF='http://nocproject.org/'>nocproject.org</A>"
        }
    ]
});