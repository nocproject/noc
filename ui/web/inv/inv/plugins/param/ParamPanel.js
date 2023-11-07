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
        // "Ext.grid.feature.Grouping",
        "NOC.inv.inv.plugins.param.ParamModel"
    ],
    title: __("Param"),
    closable: false,
    itemId: "paramPanel",
    border: false,
    initComponent: function() {
        var me = this;
        me.groupingFeature = Ext.create("Ext.grid.feature.Grouping", {startCollapsed: false});
        // Param Store
        me.store = Ext.create("Ext.data.Store", {
            model: "NOC.inv.inv.plugins.param.ParamModel",
            groupField: "scope__label",
        });
        Ext.apply(me, {
            tbar: [
                {
                    text: __("Save"),
                    glyph: NOC.glyph.save,
                    handler: me.save
                },
                {
                    text: __("Mass"),
                    itemId: "saveModeBtn",
                    enableToggle: true,
                    handler: me.changeMode
                },
                "->",
                {
                    text: __("Collapse All"),
                    handler: me.collapseAll
                },
                {
                    text: __("Expand All"),
                    handler: me.expandAll
                },
            ],
            items: [
                {
                    layout: "vbox",
                    items: [
                        {
                            layout: {
                                type: "hbox",
                                align: "stretch",
                            },
                            defaults: {
                                padding: 20,
                            },
                            border: false,
                            width: "100%",
                            items: [
                                {
                                    xtype: "combobox",
                                    store: ["Option1", "Option2", "Option3"],
                                    displayField: "component",
                                    valueField: "component",
                                    editable: false,
                                    queryMode: "local",
                                    emptyText: __("Component Sel"),
                                    flex: 1
                                },
                                {

                                    xtype: "textfield",
                                    name: "param_name",
                                    emptyText: __("Param name input"),
                                    flex: 1
                                },
                            ]
                        },
                    ]
                },
                {
                    xtype: "grid",
                    border: false,
                    autoScroll: true,
                    // stateful: true,
                    stateId: "inv.inv-param-grid",
                    bufferedRenderer: false,
                    store: me.store,
                    columns: [
                        {
                            text: __("Param"),
                            dataIndex: "param__label"
                        },
                        {
                            text: __("Scope"),
                            dataIndex: "scope__label"
                        },
                        {
                            text: __("Value"),
                            dataIndex: "value",
                            // flex: 1,
                            // editor: "textfield",
                            // getEditor: me.onGetEditor,
                            // renderer: me.onCellRender
                        },
                        {
                            text: __("Description"),
                            dataIndex: "description"
                        }
                    ],
                    features: [me.groupingFeature],
                    // selType: "cellmodel",
                    // plugins: [
                    // Ext.create("Ext.grid.plugin.CellEditing", {
                    // clicksToEdit: 2
                    // })
                    // ],
                    // viewConfig: {
                    // enableTextSelection: true
                    // },
                    // listeners: {
                    // scope: me,
                    // edit: me.onEdit
                    // }
                },
            ]
        });
        me.callParent();
    },
    // onEdit: function(editor, e, eOpts) {
    //     var me = this,
    //         toReload = e.record.get("interface") === "Common" && e.record.get("name") === "Name";

    //     console.debug("onEdit", e.record.get("interface"), e.record.get("name"));
    //     Ext.Ajax.request({
    //         url: "/inv/inv/" + me.currentId + "/plugin/param/",
    //         method: "PUT",
    //         jsonData: {
    //             "scope": e.record.get("scope"),
    //             "key": e.record.get("name"),
    //             "value": e.record.get("value")
    //         },
    //         scope: me,
    //         success: function(response) {
    //             me.onReload();
    //             if(toReload) {
    //                 me.app.onReloadNav();
    //             }
    //         },
    //         failure: function() {
    //             NOC.error(__("Failed to save"));
    //         }
    //     });
    // },
    preview: function(data) {
        var me = this;
        console.log("preview ParamPanel");
        me.store.loadData(data.data);
    },
    save: function(data) {
        var saveMode = this.up().down("[itemId=saveModeBtn]").pressed;
        console.log("save ParamPanel");
        alert("save ParamPanel mode : " + (saveMode ? "mass" : "set") + " mode");
        // Ext.Ajax.request({
        //     url: "/inv/inv/" + me.currentId + "/plugin/param/",
        //     method: "PUT",
        //     jsonData: {
        //         "mode": saveMode
        //     },
        //     scope: me,
        //     success: function(response) {
        //         me.onReload();
        //     },
        //     failure: function() {
        //         NOC.error(__("Failed to save"));
        //     }
        // });
    },
    collapseAll: function() {
        this.up("[itemId=paramPanel]").groupingFeature.collapseAll();
    },
    expandAll: function() {
        this.up("[itemId=paramPanel]").groupingFeature.expandAll();
    }
});