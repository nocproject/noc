//---------------------------------------------------------------------
// sa.serviceprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
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
                    name: "status_change_notification",
                    xtype: "combobox",
                    fieldLabel: __("Status Change Notification"),
                    allowBlank: true,
                    labelWidth: 200,
                    defaultValue: "d",
                    store: [
                        ["d", __("Disabled")],
                        ["e", __("Enable Message")],
                    ],
                    uiStyle: "medium"
                },
                {
                    xtype: "fieldset",
                    title: __("Oper. Status Transfer"),
                    items: [
                        {
                            name: "status_transfer_policy",
                            xtype: "combobox",
                            fieldLabel: __("Status Transfer Policy"),
                            tooltip: __("Transfer children Status to OperStatus <br/>" +
                                'D - Disable Status Transfer<br/>' +
                                'T - All Status transfer' +
                                'S - Self Status'),
                            store: [
                                ["D", __("Disable")],
                                ["T", __("Transparent")],
                                ["S", __("Self Status")]
                            ],
                            allowBlank: true,
                            value: "S",
                            uiStyle: "medium",
                            listeners: {
                                render: me.addTooltip
                            }
                        },

                    ]
                },
                {
                  xtype: "fieldset",
                  title: __("Calculate Oper Status"),
                  defaults: {
                    padding: 4,
                    labelAlign: "top"
                  },
                  items: [
                    {
                      name: "calculate_status_function",
                      xtype: "combobox",
                      fieldLabel: __("Calculate Oper Status Policy"),
                      tooltip: __("Calculate Oper Status <br/>" +
                          'D - Disable Calculate Status<br/>' +
                          'R - Calculate By Rule<br/>' +
                          'MN - From Min Status<br/>' +
                          'MX - From Max Status'),
                      store: [
                          ["D", __("Disable")],
                          ["MX", __("By Max Status")],
                          ["MN", __("By Min Status")],
                          ["R", __("By Rule")]
                      ],
                      allowBlank: true,
                      value: "P",
                      uiStyle: "medium",
                      listeners: {
                          render: me.addTooltip
                      }
                    },
                    {
                      name: "calculate_status_rules",
                      fieldLabel: __("Calculate Status Rules"),
                      xtype: "gridfield",
                      allowBlank: true,
                      columns: [
                        {
                            text: __("Function"),
                            dataIndex: "weight_function",
                            width: 150,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["C", "Count"],
                                    ["CP", "By Percent"],
                                    ["MIN", "Minimal"],
                                    ["MAX", "Maximum"]
                                ]
                            },
                            renderer: NOC.render.Choices({
                                "C": "Count",
                                "CP": "By Percent",
                                "MIN": "Minimal",
                                "MAX": "Maximum"
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
                            text: __("Weight"),
                            dataIndex: "weight",
                            editor: {
                                xtype: "numberfield"
                            }
                        },
                        {
                            text: __("Min. Status"),
                            dataIndex: "min_status",
                            width: 150,
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
                            text: __("Max. Status"),
                            dataIndex: "max_status",
                            width: 150,
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
                            dataIndex: "set_status",
                            width: 150,
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
                                ["A", __("By Instance")],
                                ["O", __("By Filter")]
                            ],
                            allowBlank: true,
                            value: "A",
                            uiStyle: "medium",
                            listeners: {
                                render: me.addTooltip
                            }
                        },
                        {
                            name: "alarm_status_rules",
                            fieldLabel: __("Alarm Status Rules"),
                            xtype: "gridfield",
                            allowBlank: true,
                            //width: 350,
                            columns: [
                                {
                                    dataIndex: "alarm_class_template",
                                    text: __("Alarm class RE"),
                                    editor: "textfield",
                                    width: 300,
                                    allowBlank: true
                                },
                                {
                                    text: __("Match Labels"),
                                    dataIndex: "include_labels",
                                    renderer: NOC.render.LabelField,
                                    editor: {
                                        xtype: "labelfield",
                                        query: {
                                            "allow_matched": true
                                        }
                                    },
                                    width: 200
                                },
                                {
                                    text: __("Affected Instance"),
                                    dataIndex: "affected_instance",
                                    width: 100,
                                    editor: "checkbox",
                                    renderer: NOC.render.Bool
                                },
                                {
                                    text: __("Min. Severity"),
                                    dataIndex: "min_severity",
                                    width: 200,
                                    editor: "fm.alarmseverity.LookupField",
                                    allowBlank: true,
                                    renderer: NOC.render.Lookup("min_severity")
                                },
                                {
                                    text: __("Max. Severity"),
                                    dataIndex: "max_severity",
                                    width: 200,
                                    editor: "fm.alarmseverity.LookupField",
                                    allowBlank: true,
                                    renderer: NOC.render.Lookup("max_severity")
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
                    title: __("Resource Binding"),
                    items: [
                        {
                            name: "instance_policy",
                            xtype: "combobox",
                            fieldLabel: __("Resource Map Policy"),
                            tooltip: __("How bind resources to Service Instance <br/>" +
                                'D - Disable Bind<br/>' +
                                'N - By Remote System Data' +
                                'O - By Defined Rules'),
                            store: [
                                ["D", __("Disable")],
                                ["N", __("Resource Binding")],
                                ["O", __("By Rule")]
                            ],
                            allowBlank: true,
                            value: "N",
                            uiStyle: "medium",
                            listeners: {
                                render: me.addTooltip
                            }
                        },
                        {
                            name: "instance_policy_settings",
                            fieldLabel: __("Resource Bind Rules"),
                            xtype: "gridfield",
                            allowBlank: true,
                            //width: 350,
                            columns: [
                                {
                                    text: __("Instance Type"),
                                    dataIndex: "instance_type",
                                    width: 100,
                                    editor: {
                                        xtype: "combobox",
                                        store: [
                                            ["endpoint", "Endpoint"],
                                            ["network", "Network"],
                                            ["asset", "Asset"],
                                            ["other", "Other"]
                                        ]
                                    },
                                    renderer: NOC.render.Choices({
                                        "endpoint": "L3 Endpoint",
                                        "network": "Network",
                                        "asset": "Asset",
                                        "other": "Other"
                                    })
                                },
                                {
                                    text: __("Allow Resources"),
                                    dataIndex: "allow_resources",
                                    width: 100,
                                    editor: {
                                        xtype: "tagfield",
                                        store: [
                                            ["if", "Interface"],
                                            ["si", "Subinterface"]
                                        ]
                                    },
                                    renderer: NOC.render.Choices({
                                        "if": "Interface",
                                        "si": "Subinterface"
                                    })
                                },
                                {
                                    text: __("Allow Manual"),
                                    dataIndex: "allow_manual",
                                    width: 100,
                                    editor: "checkbox",
                                    renderer: NOC.render.Bool
                                },
                                {
                                    text: __("Send Approve (To Res)"),
                                    dataIndex: "send_approve",
                                    width: 100,
                                    editor: "checkbox",
                                    renderer: NOC.render.Bool
                                },
                                {
                                    text: __("Only One Object"),
                                    dataIndex: "only_one_object",
                                    width: 100,
                                    editor: "checkbox",
                                    renderer: NOC.render.Bool
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
                            text: __("Allow Manual"),
                            dataIndex: "allow_manual",
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
