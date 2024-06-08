//---------------------------------------------------------------------
// sa.objectdiagnosticconfig application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.objectdiagnosticconfig.Application");

Ext.define("NOC.sa.objectdiagnosticconfig.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.core.ListFormField",
        "NOC.core.tagfield.Tagfield",
        "NOC.core.JSONPreview",
        "Ext.ux.form.GridField",
        "Ext.ux.form.StringsField",
        "NOC.main.ref.check.LookupField",
        "NOC.sa.objectdiagnosticconfig.LookupField",
        "NOC.fm.alarmclass.LookupField"
    ],
    model: "NOC.sa.objectdiagnosticconfig.Model",
    search: true,
    initComponent: function() {
        var me = this;

        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate('/sa/objectdiagnosticconfig/{id}/json/'),
            previewName: new Ext.XTemplate('Object Diagnostic Config: {name}')
        });

        me.ITEM_JSON = me.registerItem(me.jsonPanel);

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __('Builtin'),
                    dataIndex: 'is_builtin',
                    renderer: NOC.render.Bool,
                    width: 30
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 200
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false
                },
                {
                    name: 'uuid',
                    xtype: 'displayfield',
                    fieldLabel: __('UUID')
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    xtype: "fieldset",
                    title: __("Display Settings"),
                    layout: "hbox",
                    defaults: {
                        padding: 4
                    },
                    items: [
                        {
                            name: "display_order",
                            xtype: "numberfield",
                            fieldLabel: __("Display Order"),
                            value: 800,
                            minValue: 0,
                            allowBlank: true
                        },
                        {
                            name: "show_in_display",
                            xtype: "checkbox",
                            boxLabel: __("Show in form"),
                            tooltip: __("Display check state on Object Form"),
                            allowBlank: true,
                            listeners: {
                                render: me.addTooltip
                            }
                        }
                   ]
                },
                {
                    name: "state_policy",
                    xtype: "combobox",
                    fieldLabel: __("State Policy"),
                    tooltip: __("Policy detect diagnostic Success or Failed state <br/>" +
                                'ALL - ALL Checks and Depended Discovery must Success for Enable state<br/>' +
                                'ANY - ANY Checks and Depended Discovery mush Success for Enable state'),
                    store: [
                        ["ALL", __("ALL")],
                        ["ANY", __("ANY")]
                    ],
                    allowBlank: true,
                    value: "ANY",
                    uiStyle: "large",
                    listeners: {
                        render: me.addTooltip
                    }
                },
                {
                    name: "checks",
                    fieldLabel: __("Checks"),
                    xtype: "gridfield",
                    allowBlank: true,
                    width: 350,
                    columns: [
                        {
                            text: __("Check"),
                            dataIndex: "check",
                            width: 200,
                            editor: "main.ref.check.LookupField",
                            allowBlank: false,
                            renderer: NOC.render.Lookup("check")
                        },
                        {
                            text: __("Argument"),
                            dataIndex: "arg0",
                            editor: "textfield",
                            width: 150
                        },
                    ]
                },
                {
                    xtype: "core.tagfield",
                    url: "/sa/objectdiagnosticconfig/lookup/",
                    fieldLabel: __("Diagnostics"),
                    tooltip: __("Depended Diagnostic for calculate state"),
                    name: "diagnostics",
                    listeners: {
                        render: me.addTooltip
                    }
                },
                {
                    xtype: "fieldset",
                    title: __("Run Policy"),
                    layout: {
                        type: "table",
                        columns: 2
                    },
                    defaults: {
                        padding: 2
                    },
                    items: [
                        {
                            name: "enable_box",
                            xtype: "checkbox",
                            boxLabel: __("Enable Box"),
                            allowBlank: true
                        },
                        {
                            name: "run_policy",
                            xtype: "combobox",
                            fieldLabel: __("Run Policy"),
                            tooltip: __("Condition running diagnostic <br/>" +
                                'Always - Always run diagnostic on Discovery<br/>' +
                                'Failed - Run only Diagnoscti has Unknown or Failed state'),
                            store: [
                                ["A", __("Always")],
                                ["F", __("Unknown or Failed")]
                            ],
                            allowBlank: true,
                            value: "F",
                            uiStyle: "large",
                            listeners: {
                                render: me.addTooltip
                            }
                        },
                        {
                            name: "enable_periodic",
                            xtype: "checkbox",
                            boxLabel: __("Enable Periodic"),
                            allowBlank: true
                        },
                        {
                            name: "run_order",
                            xtype: "combobox",
                            fieldLabel: __("Run Order"),
                            tooltip: __("Order run diagnostic in Discovery process. <br/>" +
                                'On Start - Before Discovery checks run<br/>' +
                                'On End - After Discovery checks run'),
                            store: [
                                ["S", __("On Start")],
                                ["E", __("On End")]
                            ],
                            allowBlank: true,
                            value: "A",
                            uiStyle: "large",
                            listeners: {
                                render: me.addTooltip
                            }
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Alarm"),
                    items: [
                        {
                            name: "alarm_class",
                            xtype: "fm.alarmclass.LookupField",
                            fieldLabel: __("Alarm Class"),
                            tooltip: __("If set - Raise Alarm when diagnostic to Failed state"),
                            uiStyle: "large",
                            allowBlank: true,
                            listeners: {
                                render: me.addTooltip
                            }
                        },
                        {
                            name: "alarm_labels",
                            xtype: "labelfield",
                            fieldLabel: __("Alarm Labels"),
                            tooltip: __("Add setting labels to Raised Alarm. Label must <b>enable_alarm</b> setting"),
                            allowBlank: true,
                            isTree: false,
                            filterProtected: false,
                            pickerPosition: "down",
                            listeners: {
                                render: me.addTooltip
                            },
                            uiStyle: "large",
                            query: {
                                "allow_models": ["fm.Alarm"]
                            }
                        }
                    ]
                },
                {
                    name: "save_history",
                    xtype: "checkbox",
                    boxLabel: __("Save History"),
                    allowBlank: true
                },
                {
                    name: "match",
                    xtype: "listform",
                    fieldLabel: __("Match Rules"),
                    rows: 4,
                    items: [
                        {
                            name: "labels",
                            xtype: "labelfield",
                            fieldLabel: __("Match Labels"),
                            allowBlank: true,
                            isTree: true,
                            filterProtected: false,
                            pickerPosition: "down",
                            uiStyle: "extra",
                            query: {
                                "allow_matched": true
                            }
                        },
                        {
                            name: "exclude_labels",
                            xtype: "labelfield",
                            fieldLabel: __("Exclude Match Labels"),
                            allowBlank: true,
                            isTree: true,
                            filterProtected: false,
                            pickerPosition: "down",
                            uiStyle: "extra",
                            query: {
                                "allow_matched": true
                            }
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
