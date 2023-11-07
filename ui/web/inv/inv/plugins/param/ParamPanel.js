//---------------------------------------------------------------------
// inv.inv Param Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.param.ParamPanel");

Ext.define("NOC.inv.inv.plugins.param.ParamPanel", {
    extend: "Ext.panel.Panel",
    requires: [
        "NOC.inv.inv.plugins.param.ParamModel"
    ],
    title: __("Param"),
    closable: false,
    layout: "fit",

    initComponent: function() {
        var me = this;

        // Data Store
        me.store = Ext.create("Ext.data.Store", {
            model: "NOC.inv.inv.plugins.param.ParamModel",
            groupField: "interface"
        });
        // Grids
        Ext.apply(me, {
            items: [
                {
                    xtype: "displayfield",
                    value: "xxxx"
                },
                {
                    xtype: "gridpanel",
                    border: false,
                    autoScroll: true,
                    stateful: true,
                    stateId: "inv.inv-data-grid",
                    bufferedRenderer: false,
                    store: me.store,
                    region: "center",
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "name"
                        },
                        {
                            text: __("Description"),
                            dataIndex: "description"
                        },
                        {
                            scope: __("Scope"),
                            dataIndex: "scope"
                        },
                        {
                            text: __("Type"),
                            dataIndex: "type"
                        },
                        {
                            text: __("Value"),
                            dataIndex: "value",
                            flex: 1,
                            editor: "textfield",
                            getEditor: me.onGetEditor,
                            renderer: me.onCellRender
                        }
                    ],
                    features: [{
                        ftype: "grouping"
                    }],
                    selType: "cellmodel",
                    plugins: [
                        Ext.create("Ext.grid.plugin.CellEditing", {
                            clicksToEdit: 2
                        })
                    ],
                    viewConfig: {
                        enableTextSelection: true
                    },
                    listeners: {
                        scope: me,
                        edit: me.onEdit
                    }
                }
            ]
        });
        me.callParent();
    },
    onEdit: function(editor, e, eOpts) {
        var me = this,
            toReload = e.record.get("interface") === "Common" && e.record.get("name") === "Name";

        console.debug("onEdit", e.record.get("interface"), e.record.get("name"));
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/param/",
            method: "PUT",
            jsonData: {
                "interface": e.record.get("interface"),
                "key": e.record.get("name"),
                "value": e.record.get("value")
            },
            scope: me,
            success: function(response) {
                me.onReload();
                if(toReload) {
                    me.app.onReloadNav();
                }
            },
            failure: function() {
                NOC.error(__("Failed to save"));
            }
        });
    },
    preview: function(data) {
        var me = this;
        console.log("preview ParamPanel");
        me.store.loadData(data.data);
    }
});