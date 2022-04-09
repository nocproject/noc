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
        var me = this;

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
                                                    name: "metric_type",
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
                                    columnWidth: 0.4,
                                    margin: "0 20 0 0",
                                    items: [
                                        {
                                            xtype: "combobox",
                                            name: "window_function",
                                            labelAlign: "top",
                                            fieldLabel: __("Compose Function"),
                                            allowBlank: true,
                                            store: [
                                                ["disable", "Disable"],
                                                ["sumstep", "Sum Step"],
                                                ["expdecay", "Exp Decay"]
                                            ],
                                            value: "disable",
                                            listeners: {
                                                change: me.activeWindowStep
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
                                                    columns: 1,
                                                    vertical: true,
                                                    margin: "0 20 0 0",
                                                    items: [
                                                        {boxLabel: "Tick", name: "act_period", inputValue: "1"},
                                                        {
                                                            boxLabel: "Seconds",
                                                            name: "act_period",
                                                            inputValue: "2",
                                                            checked: true
                                                        },
                                                    ]
                                                },
                                                {
                                                    xtype: "numberfield",
                                                    name: "min_window",
                                                    labelAlign: "top",
                                                    fieldLabel: __("Min  Windows"),
                                                },
                                                {
                                                    xtype: "numberfield",
                                                    name: "max_window",
                                                    labelAlign: "top",
                                                    fieldLabel: __("Max  Windows"),
                                                },
                                                {
                                                    xtype: "numberfield",
                                                    itemId: "step-num",
                                                    name: "step_num",
                                                    labelAlign: "top",
                                                    fieldLabel: __("Step  Number"),
                                                    disabled: true
                                                }
                                            ]
                                        }
                                    ]
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
                                    columnWidth: 0.4,
                                    items: [
                                        {
                                            xtype: "combobox",
                                            name: "window_type",
                                            labelAlign: "top",
                                            fieldLabel: __("Compose Function"),
                                            allowBlank: true,
                                            store: [
                                                ["disable", "Disable"],
                                                ["sumstep", "Sum Step"],
                                                ["expdecay", "Exp Decay"]
                                            ],
                                            value: "disable"
                                        },
                                        {
                                            xtype: "container",
                                            layout: {
                                                type: "vbox",
                                            },
                                            minWidth: me.formMinWidth,
                                            maxWidth: me.formMaxWidth,
                                            items: [
                                                {
                                                    xtype: "radiogroup",
                                                    columns: 1,
                                                    vertical: true,
                                                    margin: "0 20 0 0",
                                                    items: [
                                                        {boxLabel: "Tick", name: "act_period", inputValue: "1"},
                                                        {
                                                            boxLabel: "Seconds",
                                                            name: "act_period",
                                                            inputValue: "2",
                                                            checked: true
                                                        },
                                                    ]
                                                },
                                                {
                                                    xtype: "numberfield",
                                                    name: "min_window",
                                                    labelAlign: "top",
                                                    fieldLabel: __("Min  Windows"),
                                                },
                                                {
                                                    xtype: "numberfield",
                                                    name: "max_window",
                                                    labelAlign: "top",
                                                    fieldLabel: __("Max  Windows"),
                                                },
                                            ]
                                        }
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
                                    title: __("Activation Activation"),
                                    width: 380,
                                    margin: "0 20 0 0",
                                    items: [
                                        {
                                            xtype: "combobox",
                                            name: "active_active_node",
                                            labelAlign: "top",
                                            fieldLabel: __("Active Node"),
                                            allowBlank: true,
                                            store: [
                                                ["disable", "Disable"],
                                                ["softplus", "Soft Plus"],
                                                ["logistic", "Logistic"]
                                            ],
                                            value: "disable"
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    itemId: "deactivation-activation",
                                    title: __("Deactivation Activation"),
                                    disabled: true,
                                    width: 400,
                                    items: [
                                        {
                                            xtype: "combobox",
                                            name: "active_active_node",
                                            labelAlign: "top",
                                            fieldLabel: __("Active Node"),
                                            allowBlank: true,
                                            store: [
                                                ["disable", "Disable"],
                                                ["softplus", "Soft Plus"],
                                                ["logistic", "Logistic"]
                                            ],
                                            value: "disable"
                                        }
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
                                    title: __("Alarm"),
                                    columnWidth: 0.4,
                                    margin: "0 20 0 0",
                                    items: [
                                        {
                                            xtype: "core.combo",
                                            name: "alarm_class",
                                            restUrl: "/fm/alarmclass/lookup/",
                                            labelAlign: "top",
                                            fieldLabel: __("Alarm Class"),
                                            allowBlank: true
                                        },
                                        {
                                            xtype: "textfield",
                                            name: "reference",
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
                                            name: "key_node",
                                            labelAlign: "top",
                                            fieldLabel: __("Key Node"),
                                            allowBlank: true,
                                            store: [
                                                ["disable", "Disable"],
                                                ["key", "Key"]
                                            ],
                                            value: "disable",
                                            listeners: {
                                                change: me.key
                                            }
                                        }
                                    ]
                                }
                            ]
                        },
                    ]
                }
                // {
                //     name: "name",
                //     xtype: "textfield",
                //     fieldLabel: __("Name"),
                //     regex: /^[a-zA-Z0-9\-\_ ]+( \| [a-zA-Z0-9\-\_ ]+)*$/
                // },
                // {
                //     name: "uuid",
                //     xtype: "displayfield",
                //     fieldLabel: __("UUID")
                // },
                // {
                //     name: "description",
                //     xtype: "textarea",
                //     fieldLabel: __("Description"),
                //     allowBlank: true
                // },
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
        var me = this;

        console.log(record);
        me.callParent([record]);
    },
    //
    addInput: function() {
        var me = this;
        me.down("[itemId=input-container]").add(Ext.create(
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
                        allowBlank: true
                    }
                ]
            }
        ));
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
    activeWindowStep: function(field, value) {
        var disable = false;

        if(value !== "sumstep") {
            disable = true;
        }
        field.up().down("[itemId=step-num]").setDisabled(disable);
    },
    //
    key: function(field, value) {
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
