//---------------------------------------------------------------------
// inv.firmwarepolicy application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.firmwarepolicy.Application");

Ext.define("NOC.inv.firmwarepolicy.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.inv.firmwarepolicy.Model",
        "NOC.inv.firmware.LookupField",
        "NOC.inv.platform.LookupField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.inv.firmwarepolicy.Model",
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Platform"),
                    dataIndex: "platform",
                    renderer: NOC.render.Lookup("platform"),
                    width: 200
                },
                {
                    text: __("Firmware"),
                    dataIndex: "firmware",
                    renderer: NOC.render.Lookup("firmware"),
                    width: 200
                },
                {
                    text: __("Condition"),
                    dataIndex: "condition",
                    width: 50
                },
                {
                    text: __("Status"),
                    dataIndex: "status",
                    width: 100,
                    renderer: NOC.render.Choices({
                        r: "Recommended",
                        a: "Acceptable",
                        n: "Not recommended",
                        d: "Denied"
                    })
                },
                {
                    text: __("Management"),
                    dataIndex: "management",
                    flex: 1,
                    renderer: function(v) {
                        return map((v || []).map(function(x) {return x.protocol;})).join(", ")
                    }
                }
            ],

            fields: [
                {
                    name: "platform",
                    xtype: "inv.platform.LookupField",
                    fieldLabel: __("Platform"),
                    allowBlank: true,
                    uiStyle: "large"
                },
                {
                    name: "firmware",
                    xtype: "inv.firmware.LookupField",
                    fieldLabel: __("Firmware"),
                    allowBlank: false,
                    uiStyle: "large"
                },
                {
                    name: "condition",
                    xtype: "combobox",
                    fieldLabel: __("Condition"),
                    store: [
                        ["<", "<"],
                        ["<=", "<="],
                        [">=", ">="],
                        [">", ">"],
                        ["=", "="],
                    ],
                    value: "=",
                    allowBlank: false,
                    uiStyle: "small"
                },
                {
                    name: "status",
                    xtype: "combobox",
                    fieldLabel: __("Status"),
                    allowBlank: false,
                    store: [
                        ["r", "Recommended"],
                        ["a", "Acceptable"],
                        ["n", "Not recommended"],
                        ["d", "Denied"]
                    ],
                    value: "a",
                    uiStyle: "medium"
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    uiStyle: "large",
                    allowBlank: true
                },
                {
                    name: "access_preference",
                    xtype: "combobox",
                    fieldLabel: __("Access Preference"),
                    tooltip: __(
                        "Preference mode with worked profile script. <br/>" +
                        "!! Work if Device Profile supported. <br/>" +
                        "Profile (default) - use Object Profile settings <br/>" +
                        "S - Use only SNMP when access to device" +
                        "CLI Only - Use only CLI when access to device" +
                        "SNMP, CLI - Use SNMP, if not avail swithc to CLI" +
                        "CLI, SNMP - Use CLI, if not avail swithc to SNMP"
                    ),
                    allowBlank: true,
                    uiStyle: "medium",
                    store: [
                        ["S", __("SNMP Only")],
                        ["C", __("CLI Only")],
                        ["SC", __("SNMP, CLI")],
                        ["CS", __("CLI, SNMP")]
                    ],
                    listeners: {
                        render: me.addTooltip
                    }
                },
                {
                    name: "snmp_rate_limit",
                    xtype: "numberfield",
                    fieldLabel: __("SNMP Rate limit"),
                    tooltip: __(
                        'Limit SNMP (Query per second).'
                    ),
                    allowBlank: true,
                    hideTrigger: true,
                    uiStyle: "medium",
                    minValue: 0,
                    maxValue: 99,
                    listeners: {
                        render: me.addTooltip
                    }
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    uiStyle: "large",
                    query: {
                        "allow_models": ["inv.FirmwarePolicy"]
                    }
                },
                {
                    name: "management",
                    xtype: "gridfield",
                    uiStyle: "medium",
                    fieldLabel: __("Management"),
                    columns: [
                        {
                            text: __("Protocol"),
                            dataIndex: "protocol",
                            flex: 1,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["cli", "CLI"],
                                    ["snmp", "SNMP"],
                                    ["http", "HTTP"]
                                ]
                            }
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
