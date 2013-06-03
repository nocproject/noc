//---------------------------------------------------------------------
// Status workplace
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.StatusPanel");

Ext.define("NOC.main.desktop.StatusPanel", {
    extend: "Ext.Panel",
    id: "status",
    region: "south",
    bodyCls: Ext.baseCSSPrefix + 'tab-bar',
    height: 20,
    maxHeight: 20,
    minHeight: 20,
    collapsible: true,
    animCollapse: true,
    collapseMode: "mini",
    split: true,
    preventHeader: true,
    layout: "hbox",
    items: [
        {
            xtype: "container",
            flex: 1
        },

        {
            xtype: "container",
            html: "&copy;2007-2013, <A HREF='http://nocproject.org/'>nocproject.org</A>"
        },

        {
            xtype: "container",
            flex: 1
        }
    ]
});