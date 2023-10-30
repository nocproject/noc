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
                    labelAlign: "top",
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID"),
                    labelAlign: "top",
                    allowBlank: true
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    labelAlign: "top",
                    allowBlank: true
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
                            editor: "textfield",
                            editor: "cm.configurationscope.LookupField",
                            renderer: NOC.render.Lookup("scope")
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
                                    ["maximum", "maximum"],
                                    ["minimum", "minimum"],
                                    ["maxLength", "maxLength"],
                                    ["minLength", "minLength"],
                                    ["pattern", "pattern"],
                                    ["step", "step"]
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
