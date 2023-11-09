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
                                triggers: {
                                    clear: {
                                        cls: 'x-form-clear-trigger',
                                        hidden: true,
                                        weight: -1,
                                        handler: function(field) {
                                            field.setValue(null);
                                        }
                                    }
                                },
                                listeners: {
                                    change: {
                                        fn: me.onFilterChange,
                                        buffer: 500
                                    }
                                }
                            },
                            border: false,
                            width: "100%",
                            items: [
                                {
                                    xtype: "combobox",
                                    name: "scope__label",
                                    displayField: "label",
                                    valueField: "id",
                                    editable: false,
                                    multiSelect: true,
                                    queryMode: "remote",
                                    emptyText: __("Component Scope"),
                                    flex: 1
                                },
                                {

                                    xtype: "textfield",
                                    name: "param__label",
                                    emptyText: __("Param name"),
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
                    stateful: true,
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
                            flex: 1,
                            editor: "textfield",
                            renderer: function(value, metaData, record) {
                                if(record.get("type") === "bool") {
                                    if(value == null) {
                                        value = false;
                                    }
                                    return NOC.render.Bool(value);
                                }
                                return value;
                            }
                        },
                        {
                            text: __("Description"),
                            dataIndex: "description"
                        }
                    ],
                    features: [me.groupingFeature],
                    selType: "cellmodel",
                    plugins: [
                        Ext.create("Ext.grid.plugin.CellEditing", {
                            clicksToEdit: 1,
                            listeners: {
                                beforeedit: function(editor, context) {
                                    var record = context.record,
                                        field = context.field,
                                        type = record.get("type"),
                                        value = record.get(field);

                                    switch(type) {
                                        case "number":
                                            context.column.setEditor({
                                                xtype: 'numberfield',
                                                step: 1,
                                                allowBlank: true
                                            });
                                            break;
                                        case "bool":
                                            context.column.setEditor({
                                                xtype: 'checkboxfield',
                                                allowBlank: true
                                            });
                                            break;
                                        default:
                                            if(record.get("choices")) {
                                                context.column.setEditor({
                                                    xtype: 'combobox',
                                                    store: {
                                                        data: Ext.Array.map(record.get("choices"), function(el) {
                                                            return {
                                                                text: el
                                                            }
                                                        })
                                                    },
                                                    valueField: 'text'
                                                });
                                            } else {
                                                context.column.setEditor({
                                                    xtype: 'textfield',
                                                    allowBlank: true
                                                });
                                            }
                                    }
                                },
                            }
                        })
                    ],
                    viewConfig: {
                        enableTextSelection: true
                    },
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
        me.down("[name=scope__label]").setStore({
            autoLoad: true,
            proxy: {
                type: "rest",
                url: "/inv/inv/" + data.id + "/plugin/param/scopes/"
            }
        });
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
    },
    onFilterChange: function(field) {
        var panel = field.up("[itemId=paramPanel]"),
            paramValue = panel.down("[name=param__label]").getValue(),
            compValue = panel.down("[name=scope__label]").getValue();

        // show/hide clear triggers
        if(paramValue == null || paramValue.length === 0) {
            panel.down("[name=param__label]").getTrigger("clear").hide();
        } else {
            panel.down("[name=param__label]").getTrigger("clear").show();
        }
        if(compValue == null || compValue.length === 0) {
            panel.down("[name=scope__label]").getTrigger("clear").hide();
        } else {
            panel.down("[name=scope__label]").getTrigger("clear").show();
        }
        // clear filter
        if((paramValue == null || paramValue.length === 0) && (compValue == null || compValue.length === 0)) {
            panel.store.clearFilter();
            return;
        }

        panel.store.clearFilter();
        panel.store.filterBy(function(record) {
            var paramCondition = function(record, paramValue) {
                return record.get("param__label").toLowerCase().includes(paramValue.toLowerCase())
            },
                scopeCondition = function(record, compValue) {
                    return compValue.filter(function(el) {return record.get("scope").toLowerCase().includes(el.toLowerCase())}).length > 0
                };
            if((paramValue && paramValue.length > 2) && (compValue == null || compValue.length === 0)) { // filter by param
                return paramCondition(record, paramValue);
            }
            if((compValue && compValue.length > 0) && (paramValue == null || paramValue.length === 0)) { // filter by scope
                return scopeCondition(record, compValue);
            }
            if((paramValue && paramValue.length > 2) && (compValue && compValue.length > 0)) { // filter by param and scope
                return paramCondition(record, paramValue) && scopeCondition(record, compValue);
            }
            return true;
        });
    }
});