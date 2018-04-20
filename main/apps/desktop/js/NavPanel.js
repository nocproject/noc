//---------------------------------------------------------------------
// Navigation panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.NavPanel");

Ext.define("NOC.main.desktop.NavPanel", {
    extend: "Ext.tree.Panel",
    region: "west",
    width: 200,
    //collapsible: true,
    animCollapse: true,
    collapseFirst: false,
    split: true,
    layout: "fit",
    app: null,
    useArrows: true,
    rootVisible: false,
    singleExpand: true,
    lines: false,
    hideHeaders: true,
    title: "Navigation",
    glyph: NOC.glyph.globe,
    store: null,
    //hidden: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            tools: [{
                type: "up",
                tooltip: "Switch to breadcrumb view",
                listeners: {
                    scope: me,
                    click: function() {me.app.toggleNav();}
                }
            }],
            listeners: {
                scope: me,
                itemclick: me.onItemClick
            }
        });
        me.callParent();
    },
    onItemClick: function(view, record, item, index, event, opts) {
        var me = this;
        me.app.launchRecord(record, !event.shiftKey);
    }
});
