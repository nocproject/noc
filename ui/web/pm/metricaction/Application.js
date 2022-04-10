//---------------------------------------------------------------------
// pm.metricaction application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricaction.Application");

Ext.define("NOC.pm.metricaction.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.pm.metricaction.Model",
        "NOC.core.JSONPreview",
        "NOC.core.ComboBox",
        "NOC.core.ListFormField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.pm.metricaction.Model",
    search: true,
    formMinWidth: 800,
    formMaxWidth: 1000,

    initComponent: function() {
        var me = this,
            windowSet = function(itemId) {
                return [
                    {
                        xtype: "combobox",
                        itemId: itemId,
                        name: itemId + ".window_function",
                        labelAlign: "top",
                        fieldLabel: __("Window Function"),
                        allowBlank: true,
                        store: [
                            ["disable", "Disable"],
                            ["sumstep", "Sum Step"],
                            ["expdecay", "Exp Decay"],
                            ["percentile", "Percentile"],
                            ["nth", "Nth"],
                        ],
                        value: "disable",
                        listeners: {
                            scope: me,
                            change: Ext.pass(me._setFieldsDisabled, {
                                fields: [
                                    {value: "sumstep", name: "window_config.direction"},
                                    {value: "expdecay", name: "window_config.factor"},
                                    {value: "nth", name: "window_config.step_num"},
                                    {value: "percentile", name: "window_config.percentile"}
                                ]
                            })
                        }
                    },
                    {
                        xtype: "container",
                        layout: {
                            type: "vbox",
                        },
                        items: [
                            {
                                xtype: "radiogroup",
                                itemId: itemId + ".window_type",
                                columns: 1,
                                vertical: true,
                                margin: "0 20 0 0",
                                items: [
                                    {
                                        boxLabel: "Tick",
                                        name: itemId + ".window_type",
                                        inputValue: "tick"
                                    },
                                    {
                                        boxLabel: "Seconds",
                                        name: itemId + ".window_type",
                                        inputValue: "seconds"
                                    },
                                ]
                            },
                            {
                                xtype: "numberfield",
                                itemId: itemId + ".min_window",
                                name: itemId + ".min_window",
                                labelAlign: "top",
                                fieldLabel: __("Min  Windows"),
                            },
                            {
                                xtype: "numberfield",
                                itemId: itemId + ".max_window",
                                name: itemId + ".max_window",
                                labelAlign: "top",
                                fieldLabel: __("Max  Windows"),
                            },
                            {
                                xtype: "radiogroup",
                                itemId: itemId + ".window_config.direction",
                                columns: 1,
                                vertical: true,
                                margin: "0 20 0 0",
                                disabled: true,
                                items: [
                                    {
                                        boxLabel: "Inc",
                                        name: itemId + ".window_config.direction",
                                        inputValue: "inc"
                                    },
                                    {
                                        boxLabel: "Desc",
                                        name: itemId + ".window_config.direction",
                                        inputValue: "dec"
                                    },
                                    {
                                        boxLabel: "Abs",
                                        name: itemId + ".window_config.direction",
                                        inputValue: "abs"
                                    },
                                ]
                            },
                            {
                                xtype: "numberfield",
                                itemId: itemId + ".window_config.factor",
                                name: itemId + ".window_config.factor",
                                labelAlign: "top",
                                fieldLabel: __("Factor"),
                                disabled: true
                            },
                            {
                                xtype: "numberfield",
                                itemId: itemId + ".window_config.percentile",
                                name: itemId + ".window_config.percentile",
                                labelAlign: "top",
                                fieldLabel: __("Percentile"),
                                disabled: true
                            },
                            {
                                xtype: "numberfield",
                                itemId: itemId + ".window_config.step_num",
                                name: itemId + ".window_config.step_num",
                                labelAlign: "top",
                                fieldLabel: __("Step  Number"),
                                disabled: true
                            }
                        ]
                    }
                ]
            },
            activationSet = function(itemId) {
                return [
                    {
                        xtype: "combobox",
                        itemId: itemId,
                        name: itemId + ".activation_function",
                        labelAlign: "top",
                        fieldLabel: __("Actition Function"),
                        allowBlank: true,
                        store: [
                            ["disable", "Disable"],
                            ["softplus", "SoftPlus"],
                            ["relu", "Relu"],
                            ["indicator", "Indicator"],
                            ["logistic", "Logistic"]
                        ],
                        value: "disable",
                        listeners: {
                            scope: me,
                            change: Ext.pass(me._setFieldsDisabled, {
                                fields: [
                                    {value: "softplus", name: "activation_config.factor"},
                                    {value: "indicator", name: "activation_config.true_level"},
                                    {value: "indicator", name: "activation_config.false_level"},
                                    {value: "logistic", name: "activation_config.lying"},
                                    {value: "logistic", name: "activation_config.stepness"},
                                ]
                            })
                        }
                    },
                    {
                        xtype: "container",
                        layout: {
                            type: "vbox",
                        },
                        items: [
                            {
                                xtype: "numberfield",
                                itemId: itemId + ".activation_config.factor",
                                name: itemId + ".activation_config.factor",
                                labelAlign: "top",
                                fieldLabel: __("Factor"),
                                disabled: true
                            },
                            {
                                xtype: "numberfield",
                                itemId: itemId + ".activation_config.true_level",
                                name: itemId + ".activation_config.true_level",
                                labelAlign: "top",
                                fieldLabel: __("True Level"),
                                disabled: true
                            },
                            {
                                xtype: "numberfield",
                                itemId: itemId + ".activation_config.false_level",
                                name: itemId + ".activation_config.false_level",
                                labelAlign: "top",
                                fieldLabel: __("False Level"),
                                disabled: true
                            },
                            {
                                xtype: "numberfield",
                                itemId: itemId + ".activation_config.lying",
                                name: itemId + ".activation_config.lying",
                                labelAlign: "top",
                                fieldLabel: __("Lying"),
                                disabled: true
                            },
                            {
                                xtype: "numberfield",
                                itemId: itemId + ".activation_config.stepness",
                                name: itemId + ".activation_config.stepness",
                                labelAlign: "top",
                                fieldLabel: __("Step  Ness"),
                                disabled: true
                            }
                        ]
                    }
                ]
            };

        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/pm/metricaction/{id}/json/'),
            previewName: new Ext.XTemplate('Metric Action: {name}')
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Builtin"),
                    dataIndex: "is_builtin",
                    renderer: NOC.render.Bool,
                    width: 50,
                    sortable: false
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                }
            ],

            fields: [
                {
                    xtype: "container",
                    itemId: "metricactionEditForm",
                    layout: "vbox",
                    items: [
                        {
                            xtype: "fieldset",
                            defaults: {
                                minWidth: me.formMinWidth - 22,
                                maxWidth: me.formMaxWidth - 22,
                            },
                            items: [
                                {
                                    name: "name",
                                    xtype: "textfield",
                                    fieldLabel: __("Name"),
                                    margin: "10 0 0 0",
                                    regex: /^[a-zA-Z0-9\-\_ ]+( \| [a-zA-Z0-9\-\_ ]+)*$/
                                },
                                {
                                    name: "uuid",
                                    xtype: "displayfield",
                                    fieldLabel: __("UUID")
                                },
                                {
                                    name: "description",
                                    xtype: "textarea",
                                    fieldLabel: __("Description"),
                                    allowBlank: true
                                }
                            ]
                        },
                        {
                            xtype: "container",
                            layout: "column",
                            minWidth: me.formMinWidth,
                            maxWidth: me.formMaxWidth,
                            items: [
                                {
                                    xtype: "fieldset",
                                    itemId: "input-container",
                                    title: __("Input"),
                                    columnWidth: 0.4,
                                    margin: "0 20 0 0",
                                    padding: "0 10 5 10",
                                    items: [
                                        {
                                            xtype: "container",
                                            layout: {
                                                type: "hbox",
                                                align: "end"
                                            },
                                            items: [
                                                {
                                                    xtype: "button",
                                                    glyph: NOC.glyph.plus,
                                                    tooltip: __("Add Input"),
                                                    scope: me,
                                                    handler: me.addInput
                                                },
                                                {
                                                    xtype: "core.combo",
                                                    name: "metric_typeF",
                                                    restUrl: "/pm/metrictype/lookup/",
                                                    labelAlign: "top",
                                                    fieldLabel: __("Metric Type"),
                                                    padding: "0 22 0 0", // 22 - addition button width
                                                    allowBlank: true
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    itemId: "compose-set",
                                    title: __("Compose"),
                                    disabled: true,
                                    columnWidth: 0.4,
                                    items: [
                                        {
                                            xtype: "combobox",
                                            name: "compose_function",
                                            labelAlign: "top",
                                            fieldLabel: __("Compose Function"),
                                            allowBlank: true,
                                            store: [
                                                ["sum", "sum"],
                                                ["avg", "avg"],
                                                ["div", "div"]
                                            ],
                                            value: "sum"
                                        },
                                        {
                                            xtype: "core.combo",
                                            name: "compose_metric_type",
                                            restUrl: "/pm/metrictype/lookup/",
                                            labelAlign: "top",
                                            fieldLabel: __("Compose Metric Type"),
                                            allowBlank: true
                                        },
                                    ]
                                },
                            ]
                        },
                        {
                            xtype: "container",
                            layout: "column",
                            minWidth: me.formMinWidth,
                            maxWidth: me.formMaxWidth,
                            items: [
                                {
                                    xtype: "fieldset",
                                    title: __("Activation Window"),
                                    layout: {
                                        type: "vbox",
                                        align: 'stretch'
                                    },
                                    width: 380,
                                    margin: "0 20 0 0",
                                    items: windowSet("activation_config")

                                },
                                {
                                    xtype: "fieldset",
                                    itemId: "deactivation-window",
                                    title: __("Deactivation Window"),
                                    disabled: true,
                                    layout: {
                                        type: "vbox",
                                        align: 'stretch'
                                    },
                                    width: 400,
                                    items: windowSet("deactivation_config")
                                },
                            ]
                        },
                        {
                            xtype: "container",
                            layout: "column",
                            minWidth: me.formMinWidth,
                            maxWidth: me.formMaxWidth,
                            items: [
                                {
                                    xtype: "fieldset",
                                    title: __("Activation"),
                                    width: 380,
                                    margin: "0 20 0 0",
                                    items: activationSet("activation_config")
                                },
                                {
                                    xtype: "fieldset",
                                    itemId: "deactivation-activation",
                                    title: __("Deactivation"),
                                    disabled: true,
                                    width: 400,
                                    items: activationSet("deactivation_config")
                                },
                            ]
                        },
                        {
                            xtype: "container",
                            layout: "column",
                            minWidth: me.formMinWidth,
                            maxWidth: me.formMaxWidth,
                            items: [
                                {
                                    xtype: "fieldset",
                                    title: __("Alarm"),
                                    columnWidth: 0.4,
                                    margin: "0 20 0 0",
                                    items: [
                                        {
                                            xtype: "core.combo",
                                            name: "alarm_config.alarm_class",
                                            restUrl: "/fm/alarmclass/lookup/",
                                            labelAlign: "top",
                                            fieldLabel: __("Alarm Class"),
                                            allowBlank: true
                                        },
                                        {
                                            xtype: "textfield",
                                            name: "alarm_config.reference",
                                            labelAlign: "top",
                                            fieldLabel: __("Reference"),
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("Key"),
                                    columnWidth: 0.4,
                                    items: [
                                        {
                                            xtype: "combobox",
                                            name: "key_function",
                                            labelAlign: "top",
                                            fieldLabel: __("Key Node"),
                                            allowBlank: true,
                                            store: [
                                                ["disable", "Disable"],
                                                ["key", "Key"]
                                            ],
                                            value: "disable",
                                            listeners: {
                                                change: me.keyFunctionChange
                                            }
                                        }
                                    ]
                                }
                            ]
                        },
                    ]
                }
            ],
            formToolbar: [
                {
                    text: __("JSON"),
                    glyph: NOC.glyph.file,
                    tooltip: __("Show JSON"),
                    hasAccess: NOC.hasPermission("read"),
                    scope: me,
                    handler: me.onJSON
                }
            ]
        });
        me.callParent();
    },
    //
    editRecord: function(record) {
        var me = this,
            i = 0,
            composeInputs = record.get('compose_inputs'),
            inputContainer = me.down("[itemId=input-container]"),
            objects = ["alarm_config", "activation_config", "deactivation_config"];

        Ext.each(objects, function(name) {
            var object = record.get(name);
            if(object) {
                Ext.Object.each(object, function(key, value) {
                    if(Ext.isObject(value)) {
                        Ext.Object.each(value, function(k, v) {
                            record.set(name + "." + key + "." + k, v);
                        })
                    } else {
                        record.set(name + "." + key, value);
                    }
                })
            }
        });
        // set initial state
        Ext.each(me.query("[name=metric_type]"), function(input) {
            inputContainer.remove(input.up());
        });
        me.down("[itemId=compose-set]").setDisabled(true);
        //
        if(composeInputs) {
            me.down("[name=metric_typeF]").setValue(composeInputs[0].metric_type);
            if(composeInputs.length > 1) {
                for(i = 1; i < composeInputs.length; i++) {
                    me.addInput(composeInputs[i].metric_type);
                }
                me.down("[itemId=compose-set]").setDisabled(false);
            }
        }
        me.callParent([record]);
    },
    //
    addInput: function(value) {
        var me = this,
            inputsContainer = me.down("[itemId=input-container]"),
            combo = Ext.create(
                {
                    xtype: "container",
                    layout: {
                        type: "hbox",
                        align: "end"
                    },
                    items: [
                        {
                            xtype: "button",
                            glyph: NOC.glyph.minus,
                            tooltip: __("Remove Input"),
                            scope: me,
                            handler: me.removeInput
                        },
                        {
                            xtype: "core.combo",
                            name: "metric_type",
                            restUrl: "/pm/metrictype/lookup/",
                            labelAlign: "top",
                            padding: "0 22 0 0", // 22 - addition button width
                            allowBlank: true,
                        }
                    ]
                }
            );
        if(value) {
            combo.down("[name=metric_type]").setValue(value);
        }
        inputsContainer.add(combo);
        me.down("[itemId=compose-set]").setDisabled(false);
    },
    //
    removeInput: function(button) {
        var inputs = button.up("[itemId=input-container]");
        inputs.remove(button.up());
        if(inputs.items.length <= 1) {
            inputs.up("[itemId=metricactionEditForm]").down("[itemId=compose-set]").setDisabled(true);
        }
    },
    //
    _setFieldsDisabled(map, field, value) {
        var itemId = field.itemId;

        Ext.each(map.fields, function(item) {
            var disable = false,
                query = "[itemId=" + itemId + "." + item.name + "]",
                element = field.up().down(query);
            if(value !== item.value) {
                disable = true;
            }
            if(element) {
                element.setDisabled(disable);
            }
        });
    },
    //
    keyFunctionChange: function(field, value) {
        var disable = false;

        if(value !== "key") {
            disable = true;
        }
        field.up("[itemId=metricactionEditForm]").down("[itemId=deactivation-activation]").setDisabled(disable);
        field.up("[itemId=metricactionEditForm]").down("[itemId=deactivation-window]").setDisabled(disable);
    },
    //
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
