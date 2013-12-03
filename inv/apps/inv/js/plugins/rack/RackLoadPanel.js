//---------------------------------------------------------------------
// inv.inv.plugins.inventory RackLoadPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.rack.RackLoadPanel");

Ext.define("NOC.inv.inv.plugins.rack.RackLoadPanel", {
    extend: "NOC.core.ApplicationPanel",
    requires: [
        "NOC.inv.inv.plugins.rack.RackLoadModel"
    ],
    app: null,
    autoScroll: true,
    layout: "fit",

    initComponent: function() {
        var me = this;

        me.store = Ext.create("Ext.data.Store", {
            model: "NOC.inv.inv.plugins.rack.RackLoadModel"
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            store: me.store,
            columns: [
                {
                    text: "Name",
                    dataIndex: "name",
                    width: 100
                },
                {
                    text: "Model",
                    dataIndex: "model",
                    width: 200
                },
                {
                    text: "Units",
                    dataIndex: "units",
                    width: 50
                },
                {
                    text: "Front pos",
                    dataIndex: "position_front",
                    width: 50,
                    editor: "numberfield"
                },
                {
                    text: "Rear pos",
                    dataIndex: "position_rear",
                    width: 50,
                    editor: "numberfield"
                },
                {
                    text: "Shift",
                    dataIndex: "shift",
                    width: 50,
                    editor: {
                        xtype: "numberfield",
                        minValue: 0,
                        maxValue: 2
                    }
                }
            ],
            selType: "cellmodel",
            plugins: [
                Ext.create("Ext.grid.plugin.CellEditing", {
                    clicksToEdit: 2
                })
            ],
            listeners: {
                scope: me,
                validateedit: Ext.bind(me.onCellValidateEdit, me),
                edit: Ext.bind(me.onCellEdit, me)
            }
        });

        Ext.apply(me, {
            items: [
                me.grid
            ]
        });
        me.callParent();
    },
    //
    preview: function(data) {
        var me = this;
        me.store.loadData(data.content);
    },
    //
    onCellValidateEdit: function(editor, e, eOpts) {
        var me = this;
        return true;
    },
    //
    onCellEdit: function(editor, e) {
        var me = this;
        console.log("EDIT", arguments);
        if(e.field == "position_front") {
            e.record.set("position_rear", 0);
        }
        if(e.field == "position_rear") {
            e.record.set("position_front", 0);
        }
        // Submit
        Ext.Ajax.request({
            url: "/inv/inv/" + me.app.currentId + "/plugin/rack/rackload/",
            method: "POST",
            scope: me,
            jsonData: {
                cid: e.record.get("id"),
                position_front: e.record.get("position_front"),
                position_rear: e.record.get("position_rear"),
                shift: e.record.get("shift")
            },
            loadMask: me,
            success: function() {
                NOC.info("Position has been changed");
                // @todo: Reset dirty flag
            },
            failure: function() {
                NOC.error("Failed to save");
            }
        });
    }
});
