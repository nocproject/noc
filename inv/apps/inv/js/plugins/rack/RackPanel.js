//---------------------------------------------------------------------
// inv.inv.plugins.inventory InventoryPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.rack.RackPanel");

Ext.define("NOC.inv.inv.plugins.rack.RackPanel", {
    extend: "NOC.core.ApplicationPanel",
    requires: [
        //"NOC.inv.inv.plugins.inventory.InventoryModel"
        "NOC.core.Rack"
    ],
    app: null,
    autoScroll: true,
    title: "Rack",
    layout: "card",

    initComponent: function() {
        var me = this;

        me.reloadButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.refresh,
            scope: me,
            tooltip: "Reload"
        });

        me.sideFrontButton = Ext.create("Ext.button.Button", {
            text: "Front",
            scope: me,
            toggleGroup: "side",
            pressed: true,
            handler: me.onEditLoad
        });

        me.sideRearButton = Ext.create("Ext.button.Button", {
            text: "Rear",
            scope: me,
            toggleGroup: "side",
            handler: me.onEditLoad
        });

        me.editLoadButton = Ext.create("Ext.button.Button", {
            text: "Edit",
            glyph: NOC.glyph.edit,
            scope: me,
            handler: me.onEditLoad,
            enableToggle: true
        });

        me.rackViewPanel = Ext.create("Ext.container.Container", {
            autoScroll: true
        });

        me.rackLoadPanel = Ext.create("NOC.inv.inv.plugins.rack.RackLoadPanel", {app: me});

        Ext.apply(me, {
            items: [
                me.rackViewPanel,
                me.rackLoadPanel
            ],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.reloadButton,
                        "-",
                        me.sideFrontButton,
                        me.sideRearButton,
                        "-",
                        me.editLoadButton
                    ]
                }
            ]
        });

        me.callParent();
    },
    //
    preview: function(data) {
        var me = this,
            r = NOC.core.Rack.getRack(5, 5, data.rack, data.content, me.getSide()),
            dc = Ext.create("Ext.draw.Component", {
                viewBox: false,
                items: r,
                autoScroll: true
            });
        me.currentId = data.id;
        me.rackViewPanel.removeAll();
        me.rackViewPanel.add(dc);
    },
    //
    getSide: function() {
        var me = this;
        return me.sideRearButton.pressed? "r" : "f";
    },
    //
    onEditLoad: function() {
        var me = this;

        if(me.editLoadButton.pressed) {
            Ext.Ajax.request({
                url: "/inv/inv/" + me.currentId + "/plugin/rack/rackload/",
                method: "GET",
                scope: me,
                success: function(response) {
                    var data = Ext.decode(response.responseText);
                    me.rackLoadPanel.preview(data);
                    me.getLayout().setActiveItem(1);
                }
            });
        } else {
            me.getLayout().setActiveItem(0);
            Ext.Ajax.request({
                url: "/inv/inv/" + me.currentId + "/plugin/rack/",
                method: "GET",
                scope: me,
                success: function(response) {
                    me.preview(Ext.decode(response.responseText));
                },
                failure: function() {
                    NOC.error("Failed to get data");
                }
            });
        }
    }
});
