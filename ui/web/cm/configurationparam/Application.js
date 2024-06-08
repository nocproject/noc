//---------------------------------------------------------------------
// cm.configurationparam application
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.configurationparam.Application");

Ext.define("NOC.cm.configurationparam.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.JSONPreview",
        "NOC.cm.configurationparam.Model",
        "NOC.cm.configurationscope.LookupField",
        "NOC.pm.measurementunits.LookupField",
        "NOC.pm.metrictype.LookupField",
        "NOC.inv.modelinterface.LookupField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.cm.configurationparam.Model",
    search: true,

    initComponent: function() {
        var me = this;

        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/cm/configurationparam/{id}/json/'),
            previewName: new Ext.XTemplate('Configuration Scope: {name}')
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 350
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "code",
                    xtype: "textfield",
                    fieldLabel: __("Code"),
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "type",
                    xtype: "combobox",
                    fieldLabel: __("Type"),
                    store: [
                        ["string", __("String")],
                        ["number", __("Number")],
                        ["bool", __("Bool")]
                    ],
                    allowBlank: false,
                    labelWidth: 200,
                    value: "string",
                    uiStyle: "large"
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
                    labelAlign: "top",
                    allowBlank: true
                },
                {
                    xtype: "fieldset",
                    title: __("Metric Threshold bind"),
                    layout: "hbox",
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "threshold_type",
                            xtype: "combobox",
                            fieldLabel: __("Threshold Type"),
                            store: [
                                ["critical_min", __("Min. Critical")],
                                ["warning_min", __("Min. Warning")],
                                ["warning_max", __("Max. Warning")],
                                ["critical_max", __("Max. Critical")]
                            ],
                            allowBlank: true,
                            labelWidth: 200,
                        },
                        {
                            name: "metric_type",
                            xtype: "pm.metrictype.LookupField",
                            fieldLabel: __("Metric Type"),
                            allowBlank: true
                        }
                    ]
                },
                {
                    name: "scopes",
                    xtype: "gridfield",
                    fieldLabel: __("Configuration Scopes"),
                    labelAlign: "top",
                    columns: [
                        {
                            dataIndex: "scope",
                            text: __("Name"),
                            editor: "cm.configurationscope.LookupField",
                            renderer: NOC.render.Lookup("scope"),
                            width: 150
                        },
                        {
                            text: __("Required"),
                            dataIndex: "is_required",
                            width: 50,
                            editor: "checkbox",
                            renderer: NOC.render.Bool
                        }
                    ]
                },
                {
                    name: "schema",
                    xtype: "gridfield",
                    fieldLabel: __("Parameters Schema"),
                    labelAlign: "top",
                    columns: [
                        {
                            dataIndex: "key",
                            text: __("Key"),
                            editor: "textfield",
                            width: 150,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["max", "Maximum"],
                                    ["min", "Minimum"],
                                    ["recommended_max", "Recommend Max"],
                                    ["recommended_min", "Recommend Minimum"],
                                    ["max_length", "Max Length"],
                                    ["min_length", "Min Length"],
                                    ["pattern", "Pattern"],
                                    ["step", "Step"],
                                    ["decimal", "Decimal"]
                                ]
                            }
                        },
                        {
                            dataIndex: "format",
                            text: __("Format"),
                            width: 70,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["date-time", "DateTime"],
                                    ["email", "email"],
                                    ["uuid", "UUID"],
                                    ["ip", "IP"]
                                ]
                            }
                        },
                        {
                            dataIndex: "value",
                            text: __("Value"),
                            editor: "textfield",
                            width: 200
                        },
                        {
                            text: __("Model Interface"),
                            dataIndex: "model_interface",
                            editor: {
                                xtype: "inv.modelinterface.LookupField",
                                forceSelection: true,
                                valueField: "label"
                            }
                        },
                        {
                            text: __("Attribute"),
                            dataIndex: "model_attr",
                            editor: "textfield"
                        }
                    ]
                },
                {
                    name: "choices",
                    xtype: "gridfield",
                    fieldLabel: __("Parameter Choices"),
                    labelAlign: "top",
                    columns: [
                        {
                            dataIndex: "name",
                            text: __("name"),
                            editor: "textfield",
                            width: 200
                        },
                        {
                            dataIndex: "value",
                            text: __("Value"),
                            editor: "textfield",
                            width: 200
                        }
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
    onJSON: function() {
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    }
});
