//---------------------------------------------------------------------
// Navigation panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.NavPanel");

Ext.define("NOC.main.desktop.NavPanel", {
    extend: "Ext.Panel",
    region: "west",
    width: 200,
    collapsible: true,
    animCollapse: true,
    collapseMode: "mini",
    split: true,
    header: false,
    layout: "fit",
    app: null,

    initComponent: function() {
        var me = this;
        me.navTreePanel = Ext.create("NOC.main.desktop.NavTree", {app: me.app});
        Ext.apply(me, {
            items: [
                me.navTreePanel
            ]
        });
        me.callParent();
    },
    //
    updateMenu: function() {
        var me = this;
        me.navTreePanel.updateMenu();
    }
});
