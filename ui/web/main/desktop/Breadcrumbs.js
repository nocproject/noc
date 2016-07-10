//---------------------------------------------------------------------
// Navigation breadcrumbs
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.Breadcrumbs");
Ext.define("NOC.main.desktop.Breadcrumbs", {
    extend: "Ext.toolbar.Toolbar",
    region: "north",
    //
    config: {
        selection: null
    },
    store: null,
    hidden: true,
    //
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            items: [
                {
                    xtype: "tool",
                    type: "down",
                    tooltip: "Switch to tree view",
                    listeners: {
                        scope: me,
                        click: function() {me.app.toggleNav();}
                    }
                },
                {
                    xtype: "breadcrumb",
                    reference: "toolbar",
                    flex: 1,
                    store: me.store,
                    listeners: {
                        scope: me,
                        selectionchange: me.onItemClick
                    }
                }
            ]
        });
        me.callParent();
        me.breadcrumbs = me.items.getAt(1);
    },
    //
    updateSelection: function(node) {
        var me = this;
        if(me.rendered) {
            me.breadcrumbs.setSelection(node);
        }
    },
    //
    onItemClick: function(bc, record, opts) {
        var me = this;
        me.app.launchRecord(record, false);
    }
});
