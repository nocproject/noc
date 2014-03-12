//---------------------------------------------------------------------
// inv.inv LAG Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.data.DataPanel");

Ext.define("NOC.inv.inv.plugins.data.DataPanel", {
    extend: "Ext.panel.Panel",
    requires: [
        "NOC.inv.inv.plugins.data.DataModel",
        "NOC.inv.inv.plugins.data.LogModel"
    ],
    title: "Data",
    closable: false,
    layout: "fit",

    initComponent: function() {
        var me = this;

        // Data Store
        me.store = Ext.create("Ext.data.Store", {
            model: "NOC.inv.inv.plugins.data.DataModel",
            groupField: "interface"
        });
        // Grids
        Ext.apply(me, {
            items: [
                {
                    xtype: "gridpanel",
                    border: false,
                    autoScroll: true,
                    stateful: true,
                    stateId: "inv.inv-data-grid",
                    store: me.store,
                    region: "center",
                    columns: [
                        {
                            text: "Name",
                            dataIndex: "name"
                        },
                        {
                            text: "Description",
                            dataIndex: "description"
                        },
                        {
                            text: "Type",
                            dataIndex: "type"
                        },
                        {
                            text: "Value",
                            dataIndex: "value",
                            flex: 1,
                            editor: "textfield",
                            getEditor: me.onGetEditor,
                            renderer: me.onCellRender
                        }
                    ],
                    features: [{ftype:'grouping'}],
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
    //
    preview: function(data) {
        var me = this;
        me.currentId = data.id;
        me.store.loadData(data.data);
    },
    //
    onReload: function() {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/data/",
            method: "GET",
            scope: me,
            success: function(response) {
                me.preview(Ext.decode(response.responseText));
            },
            failure: function() {
                NOC.error("Failed to get data");
            }
        });
    },
    //
    onEdit: function(editor, e, eOpts) {
        var me = this,
            toReload = e.record.get("interface") === "Common" && e.record.get("name") === "Name";
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/data/",
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
                NOC.error("Failed to save");
            }
        });
    },
    //
    onGetEditor: function(record) {
        if(record.get("is_const")) {
            return false;
        }
        if(record.get("choices")) {
            return {
                xtype: "combobox",
                store: record.get("choices")
            }
        }
        switch(record.get("type")) {
            case "int":
                return "numberfield";
            case "float":
                return "numberfield";
            default:
                return "textfield";
        }
    },
    //
    onCellRender: function(value, meta, record) {
        if(record.get("is_const")) {
            meta.tdCls = "noc-const";
        }
        if(record.get("type") === "bool") {
            return NOC.render.Bool(value);
        }
        return value;
    }
});
