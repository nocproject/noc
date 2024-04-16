//---------------------------------------------------------------------
// sa.serviceprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.serviceprofile.Application");

Ext.define("NOC.sa.serviceprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.sa.serviceprofile.Model",
        "NOC.sa.serviceprofile.LookupField",
        "NOC.main.ref.glyph.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.inv.interfaceprofile.LookupField",
        "NOC.inv.capability.LookupField",
        "NOC.wf.workflow.LookupField",
        "NOC.fm.alarmseverity.LookupField"
    ],
    model: "NOC.sa.serviceprofile.Model",
    search: true,
    helpId: "reference-service-profile",

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            columns: [
                {
                    text: __("Icon"),
                    dataIndex: "glyph",
                    width: 25,
                    renderer: function(v) {
                        if(v !== undefined && v !== "")
                        {
                            return "<i class='" + v + "'></i>";
                        } else {
                            return "";
                        }
                    }
                },
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 200
                },
                {
                    text: __("Code"),
                    dataIndex: "code",
                    width: 100
                },
                {
                    text: __("Workflow"),
                    dataIndex: "workflow",
                    width: 150,
                    renderer: NOC.render.Lookup("workflow")
                },
                {
                    text: __("Summary"),
                    dataIndex: "show_in_summary",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true,
                    uiStyle: "extra"
                },
                {
                    name: "code",
                    xtype: "textfield",
                    fieldLabel: __("Code"),
                    allowBlank: true,
                    uiStyle: "medium"
                },
                {
                    name: "card_title_template",
                    xtype: "textfield",
                    fieldLabel: __("Title Template"),
                    uiStyle: "extra",
                    allowBlank: true
                },
                {
                    name: "workflow",
                    xtype: "wf.workflow.LookupField",
                    fieldLabel: __("Workflow"),
                    allowBlank: false
                },
                {
                    name: "glyph",
                    xtype: "main.ref.glyph.LookupField",
                    fieldLabel: __("Icon"),
                    allowBlank: true,
                    uiStyle: "large"
                },
                {
                    name: "display_order",
                    xtype: "numberfield",
                    fieldLabel: __("Display Order"),
                    uiStyle: "small",
                    minValue: 0,
                    allowBlank: false
                },
                {
                    name: "show_in_summary",
                    xtype: "checkbox",
                    boxLabel: __("Show in summary"),
                    allowBlank: true
                },
                {
                    name: "interface_profile",
                    xtype: "inv.interfaceprofile.LookupField",
                    fieldLabel: __("Interface Profile"),
                    allowBlank: true
                },
                {
                    name: "weight",
                    xtype: "numberfield",
                    fieldLabel: __("Service weight"),
                    allowBlank: true,
                    uiStyle: "small"
                },
                {
                    xtype: "fieldset",
                    title: __("Nested Status Transfer"),
                    items: [
                        {
                            name: "status_transfer_policy",
                            xtype: "combobox",
                            fieldLabel: __("Status Transfer Policy"),
                            tooltip: __("Transfer children Status to OperStatus <br/>" +
                                'D - Disable Status Transfer<br/>' +
                                'T - All Status transfer' +
                                'R - Transfer By Rule'),
                            store: [
                                ["D", __("Disable")],
                                ["T", __("Transparent")],
                                ["R", __("By Rule")]
                            ],
                            allowBlank: true,
                            value: "T",
                            uiStyle: "medium",
                            listeners: {
                                render: me.addTooltip
                            }
                        },
                        {
                            name: "status_transfer_rule",
                            fieldLabel: __("Status Transfer Rule"),
                            xtype: "gridfield",
                            allowBlank: true,
                            columns: [
                                {
                                    text: __("Service Profile"),
                                    dataIndex: "service_profile",
                                    width: 200,
                                    editor: "sa.serviceprofile.LookupField",
                                    allowBlank: true,
                                    renderer: NOC.render.Lookup("service_profile")
                                },
                                {
                                    text: __("Op"),
                                    dataIndex: "op",
                                    width: 100,
                                    editor: {
                                        xtype: "combobox",
                                        store: [
                                            ["<=", "<="],
                                            ["=", "="],
                                            [">=", ">="]
                                        ]
                                    },
                                    renderer: NOC.render.Choices({
                                        "<=": "<=",
                                        "=": "=",
                                        ">=": ">="
                                    })
                                },
                                {
                                    text: __("Weight"),
                                    dataIndex: "weight",
                                    editor: {
                                        xtype: "numberfield"
                                    }
                                },
                                {
                                    text: __("Status"),
                                    dataIndex: "status",
                                    width: 100,
                                    editor: {
                                        xtype: "combobox",
                                        store: [
                                            [0, "UNKNOWN"],
                                            [1, "UP"],
                                            [2, "SLIGHTLY_DEGRADED"],
                                            [3, "DEGRADED"],
                                            [4, "DOWN"]
                                        ]
                                    },
                                    renderer: NOC.render.Choices({
                                        0: "UNKNOWN",
                                        1: "UP",
                                        2: "SLIGHTLY_DEGRADED",
                                        3: "DEGRADED",
                                        4: "DOWN"
                                    })
                                },
                                {
                                    text: __("To Status"),
                                    dataIndex: "to_status",
                                    width: 100,
                                    editor: {
                                        xtype: "combobox",
                                        store: [
                                            [0, "UNKNOWN"],
                                            [1, "UP"],
                                            [2, "SLIGHTLY_DEGRADED"],
                                            [3, "DEGRADED"],
                                            [4, "DOWN"]
                                        ]
                                    },
                                    renderer: NOC.render.Choices({
                                        0: "UNKNOWN",
                                        1: "UP",
                                        2: "SLIGHTLY_DEGRADED",
                                        3: "DEGRADED",
                                        4: "DOWN"
                                    })
                                }
                            ]
                        },
                        {
                            name: "status_transfer_function",
                            xtype: "combobox",
                            fieldLabel: __("Status Transfer Function"),
                            tooltip: __("Aggregate function apply to statuses <br/>" +
                                'P - Calculate status percent<br/>' +
                                'MIN - Minimal Status and Weight' +
                                'MAX - Maximum Status and Weight' +
                                'SUM - Summary Status and Weight'),
                            store: [
                                ["P", __("By Percent")],
                                ["MIN", __("Minimal")],
                                ["MAX", __("Maximal")],
                                ["SUM", __("Sum Weight")]
                            ],
                            allowBlank: true,
                            value: "MIN",
                            uiStyle: "medium",
                            listeners: {
                                render: me.addTooltip
                            }
                        },
                        {
                            name: "status_transfer_map",
                            fieldLabel: __("Status Transfer Map"),
                            xtype: "gridfield",
                            allowBlank: true,
                            columns: [
                                {
                                    text: __("Op"),
                                    dataIndex: "op",
                                    width: 100,
                                    editor: {
                                        xtype: "combobox",
                                        store: [
                                            ["<=", "<="],
                                            ["=", "="],
                                            [">=", ">="]
                                        ]
                                    },
                                    renderer: NOC.render.Choices({
                                        "<=": "<=",
                                        "=": "=",
                                        ">=": ">="
                                    })
                                },
                                {
                                    text: __("Weight"),
                                    dataIndex: "weight",
                                    editor: {
                                        xtype: "numberfield"
                                    }
                                },
                                {
                                    text: __("Min. Status"),
                                    dataIndex: "status",
                                    width: 100,
                                    editor: {
                                        xtype: "combobox",
                                        store: [
                                            [0, "UNKNOWN"],
                                            [1, "UP"],
                                            [2, "SLIGHTLY_DEGRADED"],
                                            [3, "DEGRADED"],
                                            [4, "DOWN"]
                                        ]
                                    },
                                    renderer: NOC.render.Choices({
                                        0: "UNKNOWN",
                                        1: "UP",
                                        2: "SLIGHTLY_DEGRADED",
                                        3: "DEGRADED",
                                        4: "DOWN"
                                    })
                                },
                                {
                                    text: __("To Status"),
                                    dataIndex: "to_status",
                                    width: 100,
                                    editor: {
                                        xtype: "combobox",
                                        store: [
                                            [0, "UNKNOWN"],
                                            [1, "UP"],
                                            [2, "SLIGHTLY_DEGRADED"],
                                            [3, "DEGRADED"],
                                            [4, "DOWN"]
                                        ]
                                    },
                                    renderer: NOC.render.Choices({
                                        0: "UNKNOWN",
                                        1: "UP",
                                        2: "SLIGHTLY_DEGRADED",
                                        3: "DEGRADED",
                                        4: "DOWN"
                                    })
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    title: __("Alarm Transfer"),
                    items: [
                        {
                            name: "alarm_affected_policy",
                            xtype: "combobox",
                            fieldLabel: __("Alarm Affected Policy"),
                            tooltip: __("Transfer alarm to OperStatus <br/>" +
                                'D - Disable Alarm Transfer<br/>' +
                                'A - Any alarm by Resource'),
                            store: [
                                ["D", __("Disable")],
                                ["A", __("Any")],
                                ["O", __("By Filter")]
                            ],
                            allowBlank: true,
                            value: "D",
                            uiStyle: "medium",
                            listeners: {
                                render: me.addTooltip
                            }
                        },
                        {
                            name: "alarm_status_map",
                            fieldLabel: __("Alarm Status Map"),
                            xtype: "gridfield",
                            allowBlank: true,
                            //width: 350,
                            columns: [
                                {
                                    text: __("Transfer Function"),
                                    dataIndex: "transfer_function",
                                    width: 100,
                                    editor: {
                                        xtype: "combobox",
                                        store: [
                                            ["min", "Min"],
                                            ["max", "Max"],
                                            ["percent", "Percent"]
                                        ]
                                    },
                                    renderer: NOC.render.Choices({
                                        "min": "Min",
                                        "max": "Max",
                                        "percent": "Percent"
                                    })
                                },
                                {
                                    text: __("Op"),
                                    dataIndex: "op",
                                    width: 100,
                                    editor: {
                                        xtype: "combobox",
                                        store: [
                                            ["<=", "<="],
                                            ["=", "="],
                                            [">=", ">="]
                                        ]
                                    },
                                    renderer: NOC.render.Choices({
                                        "<=": "<=",
                                        "=": "=",
                                        ">=": ">="
                                    })
                                },
                                {
                                    text: __("Percent"),
                                    dataIndex: "percent",
                                    editor: {
                                        xtype: "numberfield"
                                    }
                                },
                                {
                                    text: __("Severity"),
                                    dataIndex: "severity",
                                    width: 200,
                                    editor: "fm.alarmseverity.LookupField",
                                    allowBlank: true,
                                    renderer: NOC.render.Lookup("severity")
                                },
                                {
                                    text: __("Status"),
                                    dataIndex: "status",
                                    width: 100,
                                    editor: {
                                        xtype: "combobox",
                                        store: [
                                            [0, "UNKNOWN"],
                                            [1, "UP"],
                                            [2, "SLIGHTLY_DEGRADED"],
                                            [3, "DEGRADED"],
                                            [4, "DOWN"]
                                        ]
                                    },
                                    renderer: NOC.render.Choices({
                                        0: "UNKNOWN",
                                        1: "UP",
                                        2: "SLIGHTLY_DEGRADED",
                                        3: "DEGRADED",
                                        4: "DOWN"
                                    })
                                }

                            ]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "remote_system",
                            xtype: "main.remotesystem.LookupField",
                            fieldLabel: __("Remote System"),
                            allowBlank: true
                        },
                        {
                            name: "remote_id",
                            xtype: "textfield",
                            fieldLabel: __("Remote ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "bi_id",
                            xtype: "displayfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    uiStyle: "extra",
                    query: {
                        "allow_models": ["sa.ServiceProfile", "sa.Service"]
                    }
                },
                {
                    name: "caps",
                    xtype: "gridfield",
                    fieldLabel: __("Capabilities"),
                    allowBlank: true,
                    columns: [
                        {
                            text: __("Name"),
                            dataIndex: "capability",
                            renderer: NOC.render.Lookup("capability"),
                            width: 250,
                            editor: "inv.capability.LookupField"
                        },
                        {
                            text: __("Default Value"),
                            dataIndex: "default_value",
                            width: 150,
                            editor: "textfield"
                        },
                        {
                            text: __("Allowed Manual"),
                            dataIndex: "allowed_manual",
                            width: 150,
                            editor: "checkbox",
                            renderer: NOC.render.Bool
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
