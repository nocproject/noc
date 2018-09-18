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
        "NOC.core.Rack",
        "NOC.inv.inv.plugins.rack.RackLoadModel"
    ],
    app: null,
    scrollable: true,
    title: __("Rack"),
    layout: "border",

    initComponent: function() {
        var me = this;

        me.reloadButton = Ext.create("Ext.button.Button", {
            glyph: NOC.glyph.refresh,
            scope: me,
            tooltip: __("Reload"),
            handler: me.onReload
        });

        me.sideFrontButton = Ext.create("Ext.button.Button", {
            text: __("Front"),
            scope: me,
            toggleGroup: "side",
            pressed: true,
            handler: me.onReload
        });

        me.sideRearButton = Ext.create("Ext.button.Button", {
            text: __("Rear"),
            scope: me,
            toggleGroup: "side",
            handler: me.onReload
        });

        me.editLoadButton = Ext.create("Ext.button.Button", {
            text: __("Edit"),
            glyph: NOC.glyph.edit,
            scope: me,
            handler: me.onEdit,
            enableToggle: true
        });

        me.rackViewPanel = Ext.create("Ext.container.Container", {
            scrollable: true,
            region: "center"
        });

        me.rackLoadStore = Ext.create("Ext.data.Store", {
            model: "NOC.inv.inv.plugins.rack.RackLoadModel"
        });

        me.rackLoadPanel = Ext.create("Ext.grid.Panel", {
            store: me.rackLoadStore,
            region: "east",
            width: 500,
            hidden: true,
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 100
                },
                {
                    text: __("Model"),
                    dataIndex: "model",
                    width: 200
                },
                {
                    text: __("Units"),
                    dataIndex: "units",
                    width: 50
                },
                {
                    text: __("Front"),
                    tooltip: __("Position Front"),
                    dataIndex: "position_front",
                    width: 50,
                    editor: "numberfield"
                },
                {
                    text: __("Rear"),
                    tooltip: __("Position Rear"),
                    dataIndex: "position_rear",
                    width: 50,
                    editor: "numberfield"
                },
                {
                    text: __("Shift"),
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
            sprites = NOC.core.Rack.getRack(me, 5, 5, data.rack, data.content, me.getSide()),
            dc = Ext.create("Ext.draw.Container", {
                sprites: sprites,
                height: me.rackViewPanel.getHeight(),
                listeners: {
                    spriteclick: function(sprite, event) {
                        if(sprite.sprite.managed_object_id){
                            window.open(
                                        "/api/card/view/managedobject/" + sprite.sprite.managed_object_id + "/"
                                    );
                        }
                    }
                },
                plugins: ['spriteevents']
            });

        me.currentId = data.id;
        me.rackViewPanel.removeAll();
        me.rackViewPanel.add(dc);
        me.rackLoadStore.loadData(data.load);
    },
    //
    getSide: function() {
        var me = this;
        return me.sideRearButton.pressed? "r" : "f";
    },
    //
    onReload: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/rack/",
            method: "GET",
            scope: me,
            success: function(response) {
                me.preview(Ext.decode(response.responseText));
            },
            failure: function() {
                NOC.error(__("Failed to get data"));
            }
        });
    },
    //
    onEdit: function() {
        var me = this;

        if(me.editLoadButton.pressed) {
            me.rackLoadPanel.show();
        } else {
            me.rackLoadPanel.hide();
        }
    },
    onCellValidateEdit: function(editor, e, eOpts) {
        var me = this;
        return true;
    },
    //
    onCellEdit: function(editor, e) {
        var me = this;
        if(e.field === "position_front") {
            e.record.set("position_rear", 0);
        }
        if(e.field === "position_rear") {
            e.record.set("position_front", 0);
        }
        // Submit
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/rack/rackload/",
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
                me.onReload();
            },
            failure: function() {
                NOC.error(__("Failed to save"));
            }
        });
    },
    //
    onObjectSelect: function(objectId) {
        var me = this;
        me.app.showObject(objectId);
    }
});
