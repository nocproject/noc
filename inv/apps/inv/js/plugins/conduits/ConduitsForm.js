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
    layout: {
        type: "hbox",
        align: "stretch"
    },
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

        me.saveButton = Ext.create("Ext.button.Button", {
            text: "Save",
            glyph: NOC.glyph.save,
            scope: me,
            disabled: true,
            handler: me.onSaveConduits
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

        me.followButton = Ext.create("Ext.button.Button", {
            text: "Follow",
            glyph: NOC.glyph.long_arrow_right,
            disabled: true,
            scope: me,
            handler: me.onFollowConduits
        });

        me.ductsStore = Ext.create("Ext.data.Store", {
            model: null,
            fields: [
                "connection_id",
                "target_id", "target_name",
                "target_model", "map_distance", "project_distance",
                "conduits",
                "n_conduits", "bearing", "s_bearing"
            ],
            listeners: {
                scope: me,
                update: me.onUpdateConduits
            }
        });

        me.ductsGrid = Ext.create("Ext.grid.Panel", {
            store: me.ductsStore,
            width: 400,
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    me.saveButton,
                    "-",
                    me.addButton,
                    me.deleteButton,
                    "-",
                    me.followButton
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
                    renderer: me.renderSize,
                    editor: "textfield"
                },
                {
                    text: "Bearing",
                    dataIndex: "s_bearing",
                    width: 50
                },
                {
                    text: "Conduits",
                    dataIndex: "n_conduits",
                    width: 50,
                    align: "right"
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
                select: me.onSelectConduit
            }
        });
        //
        me.conduitsLayout = Ext.create("NOC.inv.inv.plugins.conduits.ConduitsLayoutPanel", {
            app: me
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
                me.ductsGrid,
                me.conduitsLayout
            ]
        });

        me.callParent();
    },
    //
    preview: function(data) {
        var me = this;
        me.currentId = data.id;
        me.ductsStore.loadData(data.ducts);
        me.saveButton.setDisabled(true);
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
    addConduits: function(config) {
        var me = this;
        me.ductsStore.add({
            target_id: config.target_id,
            target_name: config.target_name,
            project_distance: config.project_distance,
            map_distance: config.map_distance,
            s_bearing: config.s_bearing,
            n_conduits: 0,
            conduits: []
        });
        me.saveButton.setDisabled(false);
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
    deleteConduits: function(record) {
        var me = this;
        me.ductsStore.remove(record);
        me.saveButton.setDisabled(false);
        me.conduitsLayout.createBlockButton.setDisabled(true);
    },
    //
    onDeleteConduits: function() {
        var me = this,
            sm = me.ductsGrid.getSelectionModel(),
            selection = sm.getSelection(),
            remoteId = selection[0].get("target_id");
        Ext.Msg.show({
            title: "Remove conduits to " + selection[0].get("target_name") + "?",
            msg: "Would you like to remove conduits?",
            buttons: Ext.Msg.YESNO,
            glyph: NOC.glyph.question_sign,
            fn: function(rec) {
                if(rec == "yes") {
                    me.deleteConduits(selection[0]);
                }
            }
        });
    },
    //
    onFollowConduits: function() {
        var me = this,
            sm = me.ductsGrid.getSelectionModel(),
            selection = sm.getSelection(),
            remoteId = selection[0].get("target_id");
        me.app.app.showObject(remoteId);
    },
    //
    onSelectConduit: function(grid, record, index, eOpts) {
        var me = this;
        me.deleteButton.setDisabled(false);
        me.followButton.setDisabled(false);
        me.conduitsLayout.preview(record);
    },
    //
    reload: function() {
        var me = this;
        me.app.reload();
        me.deleteButton.setDisabled(true);
        me.followButton.setDisabled(true);
    },
    //
    reloadMapLayer: function() {
        var me = this;
        me.app.app.invPlugins.map.reloadLayer("conduits");
    },
    //
    onSaveConduits: function() {
        var me = this,
            data = [];
        me.ductsStore.each(function(v) {
            data.push({
                target: v.get("target_id"),
                project_distance: v.get("project_distance"),
                conduits: v.get("conduits")
            });
        });
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/conduits/",
            method: "POST",
            jsonData: {
                ducts: data
            },
            scope: me,
            success: function() {
                me.reloadMapLayer();
                me.reload();
            },
            failure: function() {
                NOC.error("Failed to save conduits");
            }
        });
    },
    //
    onUpdateConduits: function() {
        var me = this;
        me.saveButton.setDisabled(false);
    }
});
