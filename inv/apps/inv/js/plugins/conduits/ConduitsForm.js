//---------------------------------------------------------------------
// inv.inv Conduits form
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.conduits.ConduitsForm");

Ext.define("NOC.inv.inv.plugins.conduits.ConduitsForm", {
    extend: "Ext.panel.Panel",
    requires: [
    ],
    title: "Conduits",
    closable: false,
    layout: "fit",
    autoScroll: true,
    app: null,

    initComponent: function() {
        var me = this;

        me.closeButton = Ext.create("Ext.button.Button", {
            text: "Close",
            glyph: NOC.glyph.arrow_left,
            scope: me,
            handler: me.onClose
        });

        me.addButton = Ext.create("Ext.button.Button", {
            text: "Add",
            glyph: NOC.glyph.plus,
            scope: me,
            handler: me.onAddConduits
        });

        me.deleteButton = Ext.create("Ext.button.Button", {
            text: "Remove",
            glyph: NOC.glyph.minus,
            disabled: true,
            scope: me,
            handler: me.onDeleteConduits
        });

        me.conduitsStore = Ext.create("Ext.data.Store", {
            model: null,
            fields: [
                "target_id", "target_name",
                "target_model", "map_distance", "project_distance",
                "n_conduits"
            ]
        });

        me.conduitsGrid = Ext.create("Ext.grid.Panel", {
            store: me.conduitsStore,
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    me.addButton,
                    me.deleteButton
                ]
            }],
            columns: [
                {
                    text: "Target",
                    dataIndex: "target_name",
                    width: 100
                },
                {
                    text: "Map Distange (m)",
                    dataIndex: "map_distance",
                    width: 100,
                    align: "right",
                    renderer: me.renderSize
                },
                {
                    text: "Proj. Distange (m)",
                    dataIndex: "project_distance",
                    width: 100,
                    align: "right",
                    renderer: me.renderSize
                },
                {
                    text: "Conduits",
                    dataIndex: "n_conduits",
                    width: 50,
                    align: "right"
                }
            ],
            listeners: {
                scope: me,
                select: me.onSelectConduit
            }
        });
        //
        Ext.apply(me, {
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        me.closeButton,
                        "-"
                    ]
                }
            ],
            items: [
                me.conduitsGrid
            ]
        });

        me.callParent();
    },
    //
    preview: function(data) {
        var me = this;
        me.currentId = data.id;
        me.conduitsStore.loadData(data.conduits);
    },
    //
    onClose: function() {
        var me = this;
    },
    //
    renderSize: function(v) {
        if(v) {
            return v.toFixed(1);
        } else {
            return "-";
        }
    },
    //
    onAddConduits: function() {
        var me = this;
        // Request candidate proposals
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/conduits/get_neighbors/",
            method: "GET",
            scope: me,
            success: function(response) {
                var w = Ext.create("NOC.inv.inv.plugins.conduits.AddConduitsForm", {
                    app: me,
                    storeData: Ext.decode(response.responseText)
                });
                w.show();
            },
            failure: function() {
                NOC.error("Failed to get neighbors");
            }
        })
    },
    //
    deleteConduits: function(remoteId) {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/conduits/conduits/" + remoteId + "/",
            method: "DELETE",
            scope: me,
            success: function() {
                me.reload();
            },
            failure: function() {
                NOC.error("Failed to remove conduits");
            }
        });
    },
    //
    onDeleteConduits: function() {
        var me = this,
            sm = me.conduitsGrid.getSelectionModel(),
            selection = sm.getSelection(),
            remoteId = selection[0].get("target_id");
        Ext.Msg.show({
            title: "Remove conduits to " + selection[0].get("target_name") + "?",
            msg: "Would you like to remove conduits? Operation cannot be undone",
            buttons: Ext.Msg.YESNO,
            glyph: NOC.glyph.question_sign,
            fn: function(rec) {
                if(rec == "yes") {
                    me.deleteConduits(remoteId);
                }
            }
        });
    },
    //
    onSelectConduit: function(grid, record, index, eOpts) {
        var me = this;
        me.deleteButton.setDisabled(false);
    },
    //
    reload: function() {
        var me = this;
        me.app.reload();
        me.deleteButton.setDisabled(true);
    }
});
