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
    saveBuffer: [],
    initComponent: function() {
        var me = this;
        me.groupingFeature = Ext.create("Ext.grid.feature.Grouping", {startCollapsed: false});
        // Param Store
        me.store = Ext.create("Ext.data.Store", {
            model: "NOC.inv.inv.plugins.param.ParamModel",
            groupField: "scope__label",
        });
        me.bufferSizeText = '<span class="x-btn-inner x-btn-inner-default-toolbar-small">' + __('Buffer Size') + ' : {0}</span>';
        me.dynamicField = Ext.create({
            xtype: 'box',
            html: Ext.String.format(me.bufferSizeText, 0),
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
                    enableToggle: true
                },
                "|",
                me.dynamicField,
                "|",
                {
                    text: __("Reset"),
                    glyph: NOC.glyph.eraser,
                    handler: me.reset,
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
                                        cls: "x-form-clear-trigger",
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
                                        mappingValidationParams = function(el) {
                                            if(record.get(el.param)) {
                                                if(el.param === "regex") {
                                                    editor[el.mapTo] = new RegExp(record.get(el.param));
                                                } else if(el.param === "step") {
                                                    var step = Number(record.get(el.param));
                                                    if(!Number.isNaN(step)) {
                                                        editor[el.mapTo] = step;
                                                    }
                                                } else {
                                                    editor[el.mapTo] = record.get(el.param);
                                                }
                                            }
                                        };;

                                    if(record.get("is_readonly")) {
                                        return false;
                                    }
                                    switch(type) {
                                        case "number":
                                            var numberEditor = {
                                                xtype: "numberfield",
                                            };
                                            if(record.get("minValue") || record.get("maxValue")) {
                                                numberEditor.fieldLabel = record.get("minValue") + " - " + record.get("maxValue");
                                                if(record.get("step")) {
                                                    numberEditor.fieldLabel += "," + record.get("step");
                                                }
                                            }
                                            Ext.each([
                                                {param: "allowBlank", mapTo: "allowBlank"},
                                                {param: "maxValue", mapTo: "maxValue"},
                                                {param: "minValue", mapTo: "minValue"},
                                                {param: "step", mapTo: "step"}
                                            ],
                                                mappingValidationParams);
                                            context.column.setEditor(numberEditor);
                                            break;
                                        case "bool":
                                            var boolEditor = {
                                                xtype: "checkboxfield"
                                            };
                                            Ext.each([
                                                {param: "allowBlank", mapTo: "allowBlank"},
                                            ],
                                                mappingValidationParams);
                                            context.column.setEditor(boolEditor);
                                            break;
                                        default:
                                            if(record.get("choices")) {
                                                var defaultEditor = {
                                                    xtype: "combobox",
                                                    store: {
                                                        data: Ext.Array.map(record.get("choices"), function(el) {
                                                            return {
                                                                text: el
                                                            };
                                                        })
                                                    },
                                                    valueField: "text"
                                                };
                                                Ext.each([
                                                    {param: "allowBlank", mapTo: "allowBlank"}],
                                                    mappingValidationParams);
                                                context.column.setEditor(defaultEditor);
                                            } else {
                                                var textEditor = {
                                                    xtype: "textfield",
                                                };
                                                Ext.each([
                                                    {param: "allowBlank", mapTo: "allowBlank"},
                                                    {param: "maxLength", mapTo: "maxLength"},
                                                    {param: "minLength", mapTo: "minLength"},
                                                    {param: "regex", mapTo: "regex"}
                                                ],
                                                    mappingValidationParams);
                                                context.column.setEditor(textEditor);
                                            }
                                    }
                                }
                            }
                        })
                    ],
                    viewConfig: {
                        enableTextSelection: true
                    },
                    listeners: {
                        scope: me,
                        edit: me.onEdit
                    }
                },
            ]
        });
        me.callParent();
    },
    onEdit: function(editor, e, eOpts) {
        var record = editor.context.record,
            isMassMode = this.down("[itemId=saveModeBtn]").pressed,
            grid = this.down("[xtype=grid]");

        if(record.get("value") == null) {
            return;
        }
        if(e.originalValue === e.value) {
            return;
        }
        if(isMassMode) {
            var scope = [];
            grid.getStore().each(function(r) {
                if(r.get("param") === record.get("param")) {
                    r.set("value", record.get("value"));
                }
                Ext.Array.include(scope, r.get("scope"));
            });
            this.saveBuffer.push({param: record.get("param"), value: record.get("value"), scopes: scope});
        } else {
            const buf = {param: record.get("param"), value: record.get("value")};
            if(!Ext.isEmpty(record.get("scope"))) {
                buf.scopes = [record.get("scope")];
            }
            this.saveBuffer.push(buf);
        }
        this.dynamicField.setHtml(Ext.String.format(this.bufferSizeText, this.saveBuffer.length));
    },
    preview: function(data) {
        var me = this;
        me.currentId = data.id;
        me.store.loadData(data.data);
        me.down("[name=scope__label]").setStore({
            autoLoad: true,
            proxy: {
                type: "rest",
                url: "/inv/inv/" + data.id + "/plugin/param/scopes/"
            }
        });
    },
    save: function() {
        var me = this.up("[itemId=paramPanel]");
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/param/",
            method: "PUT",
            jsonData: me.saveBuffer,
            scope: me,
            success: function(response) {
                me.onReload();
            },
            failure: function() {
                NOC.error(__("Failed to save"));
            }
        });
    },
    onReload: function() {
        var me = this;
        me.saveBuffer = [];
        me.dynamicField.setHtml(Ext.String.format(me.bufferSizeText, me.saveBuffer.length));
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/param/",
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
    reset: function() {
        var me = this.up("[itemId=paramPanel]");
        me.onReload();
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