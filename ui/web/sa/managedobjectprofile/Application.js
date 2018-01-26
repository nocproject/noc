//---------------------------------------------------------------------
// sa.managedobjectprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobjectprofile.Application");

Ext.define("NOC.sa.managedobjectprofile.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.managedobjectprofile.Model",
        "NOC.sa.managedobjectprofile.LookupField",
        "NOC.sa.authprofile.LookupField",
        "NOC.main.style.LookupField",
        "NOC.main.ref.stencil.LookupField",
        "Ext.ux.form.MultiIntervalField",
        "NOC.pm.metrictype.LookupField",
        "NOC.main.remotesystem.LookupField"
    ],
    model: "NOC.sa.managedobjectprofile.Model",
    search: true,
    rowClassField: "row_class",
    validationModelId: "sa.ManagedObjectProfile",

    initComponent: function() {
        var me = this;

        me.ITEM_VALIDATION_SETTINGS = me.registerItem(
            Ext.create("NOC.cm.validationpolicysettings.ValidationSettingsPanel", {
                app: me,
                validationModelId: me.validationModelId
            })
        );

        me.validationSettingsButton = Ext.create("Ext.button.Button", {
            text: __("Validation"),
            glyph: NOC.glyph.file,
            scope: me,
            handler: me.onValidationSettings
        });

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name"
                },
                {
                    text: __("Level"),
                    dataIndex: "level",
                    width: 60,
                    align: "right"
                },
                {
                    text: __("Ping"),
                    dataIndex: "enable_ping",
                    width: 100,
                    renderer: function(value, meta, record) {
                        var v = NOC.render.Bool(value);
                        if(value) {
                            v += " " + NOC.render.Duration(record.get("ping_interval"));
                            if(record.get("report_ping_rtt")) {
                                v += "+RTT"
                            }
                        }
                        return v
                    },
                    align: "center"
                },
                {
                    text: __("Sync IPAM"),
                    dataIndex: "sync_ipam",
                    width: 60,
                    renderer: NOC.render.Bool,
                    align: "center"
                },
                {
                    text: __("Box discovery"),
                    dataIndex: "enable_box_discovery",
                    width: 100,
                    renderer: function(value, meta, record) {
                        var v = NOC.render.Bool(value);
                        if(value) {
                            v += " " + NOC.render.Duration(record.get("box_discovery_interval"));
                        }
                        return v
                    },
                    align: "center"
                },

//                {
//                    text: __("SLA"),
//                    dataIndex: "enable_box_discovery_sla",
//                    width: 60,
//                    renderer: NOC.render.Bool,
//                    align: "center"
//                },
//                {
//                    text: __("CPE"),
//                    dataIndex: "enable_box_discovery_cpe",
//                    width: 60,
//                    renderer: NOC.render.Bool,
//                    align: "center"
//                },

                {
                    text: __("Failed interval"),
                    dataIndex: "box_discovery_failed_interval",
                    width: 100,
                    renderer: NOC.render.Duration,
                    align: "center"
                },
                {
                    text: __("Periodic discovery"),
                    dataIndex: "enable_periodic_discovery",
                    width: 100,
                    renderer: function(value, meta, record) {
                        var v = NOC.render.Bool(value);
                        if(value) {
                            v += " " + NOC.render.Duration(record.get("periodic_discovery_interval"));
                        }
                        return v
                    },
                    align: "center"
                },
                {
                    text: __("Objects"),
                    dataIndex: "mo_count",
                    width: 60,
                    align: "right",
                    sortable: false
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
                    xtype: "tabpanel",
                    layout: "fit",
                    autoScroll: true,
                    anchor: "-0, -50",
                    defaults: {
                        autoScroll: true,
                        layout: "anchor",
                        padding: 10
                    },
                    items: [
                        {
                            title: __("Common"),
                            items: [
                                {
                                    name: "description",
                                    xtype: "textarea",
                                    fieldLabel: __("Description"),
                                    allowBlank: true,
                                    uiStyle: "extra"
                                },
                                {
                                    name: "level",
                                    xtype: "numberfield",
                                    fieldLabel: __("Level"),
                                    allowBlank: false,
                                    uiStyle: "small"
                                },
                                {
                                    name: "style",
                                    xtype: "main.style.LookupField",
                                    fieldLabel: __("Style"),
                                    allowBlank: true
                                },
                                {
                                    name: "shape",
                                    xtype: "main.ref.stencil.LookupField",
                                    fieldLabel: __("Shape"),
                                    allowBlank: true
                                },
                                {
                                    name: "name_template",
                                    xtype: "textfield",
                                    fieldLabel: __("Name template"),
                                    allowBlank: true,
                                    uiStyle: "large"
                                }
                            ]
                        },
                        {
                            title: __("Access"),
                            items: [
                                {
                                    name: "access_preference",
                                    xtype: "combobox",
                                    fieldLabel: __("Access Preference"),
                                    labelWidth: 220,
                                    allowBlank: false,
                                    uiStyle: "medium",
                                    store: [
                                        ["S", __("SNMP Only")],
                                        ["C", __("CLI Only")],
                                        ["SC", __("SNMP, CLI")],
                                        ["CS", __("CLI, SNMP")]
                                    ],
                                    value: "SC"
                                },
                                {
                                    name: "cli_session_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("CLI Session Policy"),
                                    labelWidth: 220,
                                    allowBlank: true,
                                    labelAlign: "left",
                                    uiStyle: "medium",
                                    store: [
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    value: "E"
                                },
                                {
                                    name: "cli_privilege_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("CLI Privilege Policy"),
                                    labelWidth: 220,
                                    allowBlank: true,
                                    uiStyle: "medium",
                                    store: [
                                        ["D", __("Do not raise")],
                                        ["E", __("Raise Privileges")]
                                    ],
                                    value: "E"
                                }
                            ]
                        },
                        {
                            title: __("Card"),
                            items: [
                                {
                                    name: "card",
                                    xtype: "textfield",
                                    fieldLabel: __("Card"),
                                    labelWidth: 200,
                                    allowBlank: true,
                                    uiStyle: "extra"
                                },
                                {
                                    name: "card_title_template",
                                    xtype: "textfield",
                                    fieldLabel: __("Card Title Template"),
                                    labelWidth: 200,
                                    allowBlank: false,
                                    uiStyle: "extra"
                                }
                            ]
                        },
                        {
                            title: "IPAM",
                            items: [
                                {
                                    name: "sync_ipam",
                                    xtype: "checkboxfield",
                                    boxLabel: __("Enable IPAM synchronization"),
                                    allowBlank: false
                                },
                                {
                                    name: "fqdn_template",
                                    xtype: "textarea",
                                    fieldLabel: __("FQDN template"),
                                    allowBlank: true,
                                    uiStyle: "extra"
                                }
                            ]
                        },
                        {
                            title: __("Ping Check"),
                            items: [
                                {
                                    name: "enable_ping",
                                    xtype: "checkboxfield",
                                    boxLabel: __("Enable"),
                                    allowBlank: false

                                },
                                {
                                    xtype: "fieldset",
                                    title: __("Ping discovery intervals"),
                                    layout: "vbox",
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "ping_interval",
                                                    xtype: "numberfield",
                                                    fieldLabel: __("Interval, sec"),
                                                    uiStyle: "small",
                                                    listeners: {
                                                        scope: me,
                                                        change: function(_item, newValue, oldValue, eOpts) {
                                                            me.form.findField("ping_calculated").setValue(newValue);
                                                        }
                                                    }
                                                },
                                                {
                                                    name: 'ping_calculated',
                                                    xtype: 'displayfield',
                                                    renderer: NOC.render.Duration
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("Ping series settings"),
                                    layout: "vbox",
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            name: "ping_policy",
                                            xtype: "combobox",
                                            labelAlign: "left",
                                            labelWidth: 220,
                                            fieldLabel: __("Ping Policy"),
                                            allowBlank: true,
                                            uiStyle: "medium",
                                            store: [
                                                ["f", __("First Success")],
                                                ["a", __("All Success")]
                                            ],
                                            value: "f"
                                        },
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "ping_size",
                                                    xtype: "numberfield",
                                                    fieldLabel: __("Packet size, bytes"),
                                                    labelWidth: 220,
                                                    uiStyle: "small",
                                                    defautlValue: 64,
                                                    minValue: 64
                                                }
                                            ]
                                        },
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "ping_count",
                                                    xtype: "numberfield",
                                                    fieldLabel: __("Packets count"),
                                                    labelWidth: 220,
                                                    defautlValue: 3,
                                                    uiStyle: "small"
                                                }
                                            ]
                                        },
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "ping_timeout_ms",
                                                    xtype: "numberfield",
                                                    fieldLabel: __("Timeout, msec"),
                                                    defaultValue: 1000,
                                                    labelWidth: 220,
                                                    uiStyle: "small",
                                                    listeners: {
                                                        scope: me,
                                                        change: function(_item, newValue, oldValue, eOpts) {
                                                            me.form.findField("ping_tm_calculated").setValue(newValue / 1000);
                                                        }
                                                    }
                                                },
                                                {
                                                    name: 'ping_tm_calculated',
                                                    xtype: 'displayfield',
                                                    renderer: NOC.render.Duration
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    name: "report_ping_rtt",
                                    xtype: "checkboxfield",
                                    boxLabel: __("Report ping RTT"),
                                    allowBlank: false
                                },
                                {
                                    name: "report_ping_attempts",
                                    xtype: "checkboxfield",
                                    boxLabel: __("Report ping attempts"),
                                    allowBlank: false
                                }
                            ]
                        },
                        {
                            title: "FM",
                            items: [
                                {
                                    name: "event_processing_policy",
                                    xtype: "combobox",
                                    labelWidth: 150,
                                    fieldLabel: __("Event Policy"),
                                    store: [
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    value: "E",
                                    allowBlank: false,
                                    uiStyle: "medium"
                                },
                                {
                                    name: "weight",
                                    xtype: "numberfield",
                                    labelWidth: 150,
                                    fieldLabel: __("Alarm Weight"),
                                    allowBlank: false,
                                    uiStyle: "small"
                                }
                            ]
                        },
                        {
                            title: __("Box discovery"),
                            items: [
                                {
                                    name: "enable_box_discovery",
                                    xtype: "checkbox",
                                    boxLabel: __("Enable")
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("Box discovery intervals"),
                                    layout: "vbox",
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "box_discovery_interval",
                                                    xtype: "numberfield",
                                                    fieldLabel: __("Interval, sec"),
                                                    labelWidth: 200,
                                                    allowBlank: false,
                                                    uiStyle: "small",
                                                    listeners: {
                                                        scope: me,
                                                        change: function(_item, newValue, oldValue, eOpts) {
                                                            me.form.findField("box_discovery_interval_calculated").setValue(newValue);
                                                        }
                                                    }
                                                },
                                                {
                                                    name: 'box_discovery_interval_calculated',
                                                    xtype: 'displayfield',
                                                    renderer: NOC.render.Duration
                                                }
                                            ]
                                        },
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "box_discovery_failed_interval",
                                                    xtype: "numberfield",
                                                    fieldLabel: __("Failed Interval, sec"),
                                                    labelWidth: 200,
                                                    allowBlank: false,
                                                    uiStyle: "small",
                                                    listeners: {
                                                        scope: me,
                                                        change: function(_item, newValue, oldValue, eOpts) {
                                                            me.form.findField("box_discovery_failed_interval_calculated").setValue(newValue);
                                                        }
                                                    }
                                                },
                                                {
                                                    name: 'box_discovery_failed_interval_calculated',
                                                    xtype: 'displayfield',
                                                    renderer: NOC.render.Duration
                                                }
                                            ]
                                        },
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "box_discovery_on_system_start",
                                                    xtype: "checkbox",
                                                    width: 250,
                                                    boxLabel: __("Check on system start after ")
                                                },
                                                {
                                                    name: "box_discovery_system_start_delay",
                                                    xtype: "numberfield",
                                                    allowBlank: false,
                                                    uiStyle: "small"
                                                },
                                                {
                                                    name: "_box_discovery_system_start_delay",
                                                    xtype: 'displayfield',
                                                    value: __("sec")
                                                }
                                            ]
                                        },
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "box_discovery_on_config_changed",
                                                    xtype: "checkbox",
                                                    width: 250,
                                                    boxLabel: __("Check on config change after ")
                                                },
                                                {
                                                    name: "box_discovery_config_changed_delay",
                                                    xtype: "numberfield",
                                                    allowBlank: false,
                                                    uiStyle: "small"
                                                },
                                                {
                                                    name: "_box_discovery_config_changed_delay",
                                                    xtype: 'displayfield',
                                                    value: __("sec")
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("Box"),
                                    layout: "hbox",
                                    defaults: {
                                        padding: "0 8 0 0"
                                    },
                                    items: [
                                        {
                                            name: "enable_box_discovery_profile",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Profile")
                                        },
                                        {
                                            name: "enable_box_discovery_version",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Version")
                                        },
                                        {
                                            name: "enable_box_discovery_caps",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Caps")
                                        },
                                        {
                                            name: "enable_box_discovery_interface",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Interface")
                                        },
                                        {
                                            name: "enable_box_discovery_prefix",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Prefix")
                                        },
                                        {
                                            name: "enable_box_discovery_id",
                                            xtype: "checkboxfield",
                                            boxLabel: __("ID")
                                        },
                                        {
                                            name: "enable_box_discovery_config",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Config")
                                        },
                                        {
                                            name: "enable_box_discovery_asset",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Asset")
                                        },
                                        {
                                            name: "enable_box_discovery_vlan",
                                            xtype: "checkboxfield",
                                            boxLabel: __("VLAN")
                                        },
                                        {
                                            name: "enable_box_discovery_mac",
                                            xtype: "checkboxfield",
                                            boxLabel: __("MAC")
                                        },
                                        {
                                            name: "enable_box_discovery_metrics",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Metrics")
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("Topology"),
                                    layout: "vbox",
                                    items: [
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "enable_box_discovery_nri",
                                                    xtype: "checkboxfield",
                                                    boxLabel: __("NRI")
                                                },
                                                {
                                                    name: "enable_box_discovery_bfd",
                                                    xtype: "checkboxfield",
                                                    boxLabel: __("BFD")
                                                },
                                                {
                                                    name: "enable_box_discovery_cdp",
                                                    xtype: "checkboxfield",
                                                    boxLabel: __("CDP")
                                                },
                                                {
                                                    name: "enable_box_discovery_huawei_ndp",
                                                    xtype: "checkboxfield",
                                                    boxLabel: __("Huawei NDP")
                                                },
                                                {
                                                    name: "enable_box_discovery_mikrotik_ndp",
                                                    xtype: "checkboxfield",
                                                    boxLabel: __("MikroTik NDP")
                                                },
                                                {
                                                    name: "enable_box_discovery_fdp",
                                                    xtype: "checkboxfield",
                                                    boxLabel: __("FDP")
                                                },
                                                {
                                                    name: "enable_box_discovery_lldp",
                                                    xtype: "checkboxfield",
                                                    boxLabel: __("LLDP")
                                                },
                                                {
                                                    name: "enable_box_discovery_oam",
                                                    xtype: "checkboxfield",
                                                    boxLabel: __("OAM")
                                                },
                                                {
                                                    name: "enable_box_discovery_rep",
                                                    xtype: "checkboxfield",
                                                    boxLabel: __("REP")
                                                },
                                                {
                                                    name: "enable_box_discovery_stp",
                                                    xtype: "checkboxfield",
                                                    boxLabel: __("STP")
                                                },
                                                {
                                                    name: "enable_box_discovery_udld",
                                                    xtype: "checkboxfield",
                                                    boxLabel: __("UDLD")
                                                },
                                                {
                                                    name: "enable_box_discovery_lacp",
                                                    xtype: "checkboxfield",
                                                    boxLabel: __("LACP")
                                                }
                                            ]
                                        },
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "neighbor_cache_ttl",
                                                    xtype: "numberfield",
                                                    fieldLabel: __("Cache neighbors for"),
                                                    allowBlank: false,
                                                    labelWidth: 130,
                                                    uiStyle: "small",
                                                    align: "right"
                                                },
                                                {
                                                    xtype: "displayfield",
                                                    name: "_neighbor_cache_ttl",
                                                    value: __("sec")
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("IPAM"),
                                    layout: "hbox",
                                    defaults: {
                                        padding: "0 8 0 0"
                                    },
                                    items: [
                                        {
                                            name: "enable_box_discovery_vrf",
                                            xtype: "checkboxfield",
                                            boxLabel: __("VRF")
                                        },
                                        {
                                            name: "enable_box_discovery_prefix_interface",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Prefix (Interface)")
                                        },
                                        {
                                            name: "enable_box_discovery_prefix",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Prefix (Neighbors)")
                                        },
                                        {
                                            name: "enable_box_discovery_address_interface",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Address (Interface)")
                                        },
                                        {
                                            name: "enable_box_discovery_address",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Address (Neighbors)")
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("Clear links"),
                                    layout: "hbox",
                                    defaults: {
                                        padding: "0 8 0 0"
                                    },
                                    items: [
                                        {
                                            name: "clear_links_on_platform_change",
                                            xtype: "checkboxfield",
                                            boxLabel: __("On platform change")
                                        }
                                        /* Not implemented yet
                                        {
                                            name: "clear_links_on_serial_change",
                                            xtype: "checkboxfield",
                                            boxLabel: __("On serial change")
                                        } */
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("SLA"),
                                    layout: "hbox",
                                    defaults: {
                                        padding: "0 8 0 0"
                                    },
                                    items: [
                                        {
                                            name: "enable_box_discovery_sla",
                                            xtype: "checkboxfield",
                                            boxLabel: __("SLA")
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("CPE"),
                                    layout: "vbox",
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "enable_box_discovery_cpe",
                                                    xtype: "checkboxfield",
                                                    boxLabel: __("CPE")
                                                }
                                            ]
                                        },
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "cpe_segment_policy",
                                                    xtype: "combobox",
                                                    fieldLabel: __("Segment Policy"),
                                                    allowBlank: true,
                                                    store: [
                                                        ["C", _("Use Controller's")],
                                                        ["L", _("Use uplink object's")]
                                                    ],
                                                    uiStyle: "medium"
                                                },
                                                {
                                                    name: "cpe_cooldown",
                                                    xtype: "numberfield",
                                                    fieldLabel: __("CPE Cooldown (days)"),
                                                    labelWidth: 205,
                                                    allowBlank: true,
                                                    minValue: 0,
                                                    uiStyle: "small"
                                                }
                                            ]
                                        },
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "cpe_profile",
                                                    xtype: "sa.managedobjectprofile.LookupField",
                                                    fieldLabel: __("CPE Profile"),
                                                    allowBlank: true,
                                                    uiStyle: "medium"
                                                },
                                                {
                                                    name: "cpe_auth_profile",
                                                    xtype: "sa.authprofile.LookupField",
                                                    fieldLabel: __("CPE Auth Profile"),
                                                    allowBlank: true,
                                                    uiStyle: "medium"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("Housekeeping"),
                                    layout: "hbox",
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            name: "enable_box_discovery_hk",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Housekeeping")
                                        },
                                        {
                                            name: "hk_handler",
                                            xtype: "textfield",
                                            labelAlign: "left",
                                            fieldLabel: __("Handler"),
                                            allowBlank: true
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    layout: "hbox",
                                    title: __("Discovery Alarm"),
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            name: "box_discovery_alarm_policy",
                                            xtype: "combobox",
                                            fieldLabel: __("Box Alarm"),
                                            allowBlank: true,
                                            labelWidth: 135,
                                            labelAlign: "left",
                                            uiStyle: "medium",
                                            store: [
                                                ["E", __("Enable")],
                                                ["D", __("Disable")]
                                            ],
                                            value: "D"
                                        },
                                        {
                                            name: "box_discovery_fatal_alarm_weight",
                                            xtype: "numberfield",
                                            fieldLabel: __("Fatal Alarm Weight"),
                                            labelWidth: 150,
                                            labelAlign: "left",
                                            allowBlank: true,
                                            minValue: 0,
                                            uiStyle: "small"
                                        },
                                        {
                                            name: "box_discovery_alarm_weight",
                                            xtype: "numberfield",
                                            fieldLabel: __("Alarm Weight"),
                                            labelWidth: 80,
                                            labelAlign: "left",
                                            allowBlank: true,
                                            minValue: 0,
                                            uiStyle: "small"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            title: __("Periodic discovery"),
                            items: [
                                {
                                    name: "enable_periodic_discovery",
                                    xtype: "checkbox",
                                    boxLabel: __("Enable")
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("Periodic discovery intervals"),
                                    layout: "vbox",
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            xtype: "container",
                                            layout: "hbox",
                                            defaults: {
                                                padding: "0 8 0 0"
                                            },
                                            items: [
                                                {
                                                    name: "periodic_discovery_interval",
                                                    xtype: "numberfield",
                                                    fieldLabel: __("Interval, sec"),
                                                    allowBlank: false,
                                                    uiStyle: "small",
                                                    listeners: {
                                                        scope: me,
                                                        change: function(_item, newValue, oldValue, eOpts) {
                                                            me.form.findField("periodic_discovery_interval_calculated").setValue(newValue);
                                                        }
                                                    }
                                                },
                                                {
                                                    name: 'periodic_discovery_interval_calculated',
                                                    xtype: 'displayfield',
                                                    renderer: NOC.render.Duration
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    xtype: "container",
                                    layout: {
                                        type: "table",
                                        columns: 4
                                    },
                                    defaults: {
                                        padding: "4 8 0 0"
                                    },
                                    items: [
                                        {
                                            name: "enable_periodic_discovery_uptime",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Uptime")
                                        },
                                        {
                                            name: "enable_periodic_discovery_interface_status",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Interface status")
                                        },
                                        {
                                            name: "enable_periodic_discovery_mac",
                                            xtype: "checkboxfield",
                                            boxLabel: __("MAC")
                                        },
                                        {
                                            name: "enable_periodic_discovery_metrics",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Metrics")
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    layout: "hbox",
                                    title: __("Discovery Alarm"),
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            name: "periodic_discovery_alarm_policy",
                                            xtype: "combobox",
                                            fieldLabel: __("Periodic Alarm"),
                                            allowBlank: true,
                                            labelWidth: 135,
                                            labelAlign: "left",
                                            uiStyle: "medium",
                                            store: [
                                                ["E", __("Enable")],
                                                ["D", __("Disable")]
                                            ],
                                            value: "D"
                                        },
                                        {
                                            name: "periodic_discovery_fatal_alarm_weight",
                                            xtype: "numberfield",
                                            fieldLabel: __("Fatal Alarm Weight"),
                                            labelWidth: 150,
                                            labelAlign: "left",
                                            allowBlank: true,
                                            minValue: 0,
                                            uiStyle: "small"
                                        },
                                        {
                                            name: "periodic_discovery_alarm_weight",
                                            xtype: "numberfield",
                                            fieldLabel: __("Alarm Weight"),
                                            labelWidth: 80,
                                            labelAlign: "left",
                                            allowBlank: true,
                                            minValue: 0,
                                            uiStyle: "small"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            title: __("Metrics"),
                            items: [
                                {
                                    name: "metrics",
                                    xtype: "gridfield",
                                    fieldLabel: __("Metrics"),
                                    columns: [
                                        {
                                            text: __("Metric Type"),
                                            dataIndex: "metric_type",
                                            width: 150,
                                            editor: {
                                                xtype: "pm.metrictype.LookupField"
                                            },
                                            renderer: NOC.render.Lookup("metric_type")
                                        },
                                        {
                                            text: __("Box"),
                                            dataIndex: "enable_box",
                                            width: 50,
                                            renderer: NOC.render.Bool,
                                            editor: "checkbox"
                                        },
                                        {
                                            text: __("Periodic"),
                                            dataIndex: "enable_periodic",
                                            width: 50,
                                            renderer: NOC.render.Bool,
                                            editor: "checkbox"
                                        },
                                        {
                                            text: __("Is Stored"),
                                            dataIndex: "is_stored",
                                            width: 50,
                                            renderer: NOC.render.Bool,
                                            editor: "checkbox"
                                        },
                                        {
                                            text: __("Window Type"),
                                            dataIndex: "window_type",
                                            width: 80,
                                            editor: {
                                                xtype: "combo",
                                                editable: false,
                                                // mode: "local",
                                                // value: "m",
                                                // displayField: 'text',
                                                // valueField: 'value',
                                                store: [
                                                    ["m", "Measurements"],
                                                    ["t", "Time"]
                                                ]
                                            },
                                            align: "right"
                                        },
                                        {
                                            text: __("Window"),
                                            dataIndex: "window",
                                            width: 60,
                                            editor: "textfield",
                                            align: "right"
                                        },
                                        {
                                            text: __("Window Function"),
                                            dataIndex: "window_function",
                                            width: 70,
                                            editor: {
                                                xtype: "combobox",
                                                store: [
                                                    ["last", "Last Value"],
                                                    ["avg", "Average"],
                                                    ["percentile", "Percentile"],
                                                    ["q1", "1st quartile"],
                                                    ["q2", "2st quartile"],
                                                    ["q3", "3st quartile"],
                                                    ["p95", "95% percentile"],
                                                    ["p99", "99% percentile"],
                                                    ["handler", "Handler"]
                                                ]
                                            }
                                        },
                                        {
                                            text: __("Config"),
                                            dataIndex: "window_config",
                                            width: 80,
                                            editor: "textfield"
                                            //value: ""
                                        },
                                        {
                                            text: __("Low Error"),
                                            dataIndex: "low_error",
                                            width: 60,
                                            editor: "textfield",
                                            align: "right",
                                            renderer: NOC.render.Size
                                        },
                                        {
                                            text: __("Low Warn"),
                                            dataIndex: "low_warn",
                                            width: 60,
                                            editor: "textfield",
                                            align: "right",
                                            renderer: NOC.render.Size
                                        },
                                        {
                                            text: __("High Warn"),
                                            dataIndex: "high_warn",
                                            width: 60,
                                            editor: "textfield",
                                            align: "right",
                                            renderer: NOC.render.Size
                                        },
                                        {
                                            text: __("High Error"),
                                            dataIndex: "high_error",
                                            width: 60,
                                            editor: "textfield",
                                            align: "right",
                                            renderer: NOC.render.Size
                                        }
                                        /*
                                        {
                                            text: __("Low Error Weight"),
                                            dataIndex: "low_error_weight",
                                            width: 60,
                                            editor: "textfield",
                                            align: "right",
                                            renderer: NOC.render.Size
                                        },
                                        {
                                            text: __("Low Warn Wight"),
                                            dataIndex: "low_warn_weight",
                                            width: 60,
                                            editor: "textfield",
                                            align: "right",
                                            renderer: NOC.render.Size
                                        },
                                        {
                                            text: __("High Warn Wight"),
                                            dataIndex: "high_warn_weight",
                                            width: 60,
                                            editor: "textfield",
                                            align: "right",
                                            renderer: NOC.render.Size
                                        },
                                        {
                                            text: __("High Error Wight"),
                                            dataIndex: "high_error_weight",
                                            width: 60,
                                            editor: "textfield",
                                            align: "right",
                                            renderer: NOC.render.Size
                                        }
                                        */

                                    ]

                                }
                            ]
                        },
                        {
                            title: __("MAC"),
                            items: [
                                {
                                    name: "mac_collect_all",
                                    xtype: "checkbox",
                                    boxLabel: __("Collect All"),
                                    allowBlank: true
                                },
                                {
                                    name: "mac_collect_interface_profile",
                                    xtype: "checkbox",
                                    boxLabel: __("Collect if permitted by interface profile"),
                                    allowBlank: true
                                },
                                {
                                    name: "mac_collect_management",
                                    xtype: "checkbox",
                                    boxLabel: __("Collect from management VLAN"),
                                    allowBlank: true
                                },
                                {
                                    name: "mac_collect_multicast",
                                    xtype: "checkbox",
                                    boxLabel: __("Collect from multicast VLAN"),
                                    allowBlank: true
                                },
                                {
                                    name: "mac_collect_vcfilter",
                                    xtype: "checkbox",
                                    boxLabel: __("Collect from VLAN matching VC Filter"),
                                    allowBlank: true
                                }
                            ]
                        },
                        {
                            title: __("Autosegmentation"),
                            items: [
                                {
                                    name: "autosegmentation_policy",
                                    xtype: "combobox",
                                    labelWidth: 150,
                                    fieldLabel: __("Policy"),
                                    allowBlank: false,
                                    store: [
                                        ["d", __("Do not segmentate")],
                                        ["e", __("Allow autosegmentation")],
                                        ["o", __("Segmentate for object's segment")],
                                        ["c", __("Segmentate for child segment")]
                                    ],
                                    uiStyle: "medium"
                                },
                                {
                                    name: "autosegmentation_level_limit",
                                    xtype: "numberfield",
                                    labelWidth: 150,
                                    fieldLabel: __("Level Limit"),
                                    allowBlank: false,
                                    uiStyle: "small"
                                },
                                {
                                    name: "autosegmentation_segment_name",
                                    xtype: "textfield",
                                    labelWidth: 150,
                                    fieldLabel: __("Segment Name"),
                                    allowBlank: true,
                                    uiStyle: "extra"
                                }
                            ]
                        },
                        {
                            title: __("Integration"),
                            items: [
                                {
                                    name: "remote_system",
                                    xtype: "main.remotesystem.LookupField",
                                    labelWidth: 150,
                                    fieldLabel: __("Remote System"),
                                    allowBlank: true
                                },
                                {
                                    name: "remote_id",
                                    xtype: "textfield",
                                    labelWidth: 150,
                                    fieldLabel: __("Remote ID"),
                                    allowBlank: true,
                                    uiStyle: "medium"
                                },
                                {
                                    name: "bi_id",
                                    xtype: "displayfield",
                                    labelWidth: 150,
                                    fieldLabel: __("BI ID"),
                                    allowBlank: true,
                                    uiStyle: "medium"
                                }
                            ]
                        },
                        {
                            title: __("Escalation"),
                            items: [
                                {
                                    name: "escalation_policy",
                                    xtype: "combobox",
                                    labelWidth: 150,
                                    fieldLabel: __("Escalation Policy"),
                                    allowBlank: true,
                                    uiStyle: "medium",
                                    store: [
                                        ["E", __("Enable")],
                                        ["D", __("Disable")],
                                        ["R", __("As Depended")]
                                    ],
                                    value: "E"
                                }
                            ]
                        },
                        {
                            title: __("Telemetry"),
                            items: [
                                {
                                    name: "box_discovery_telemetry_sample",
                                    xtype: "numberfield",
                                    labelWidth: 150,
                                    fieldLabel: __("Box Sample"),
                                    allowBlank: false,
                                    uiStyle: "medium"
                                },
                                {
                                    name: "periodic_discovery_telemetry_sample",
                                    xtype: "numberfield",
                                    labelWidth: 150,
                                    fieldLabel: __("Periodic Sample"),
                                    allowBlank: false,
                                    uiStyle: "medium"
                                }
                            ]
                        }
                    ]
                }
            ],
            formToolbar: [
                me.validationSettingsButton
            ]
        });
        me.callParent();
    },
    //
    filters: [
        {
            title: __("Box Discovery"),
            ftype: "list",
            listStore: {
                sorters: "label",
                data: [
                    {field_name: "enable_box_discovery_profile", label: __("Pofile")},
                    {field_name: "enable_box_discovery_version", lLabel: __("Version")},
                    {field_name: "enable_box_discovery_caps", label: __("Caps")},
                    {field_name: "enable_box_discovery_interface", label: __("Interface")},
                    {field_name: "enable_box_discovery_prefix", label: __("Prefix")},
                    {field_name: "enable_box_discovery_id", label: __("ID")},
                    {field_name: "enable_box_discovery_config", label: __("Config")},
                    {field_name: "enable_box_discovery_asset", label: __("Asset")},
                    {field_name: "enable_box_discovery_vlan", label: __("VLAN")},
                    {field_name: "enable_box_discovery_mac", label: __("MAC")},
                    {field_name: "enable_box_discovery_metrics", label: __("Metrics")}
                ]
            },
            valuesStore: {
                sorters: "label",
                data: [
                    {label: __('Enabled'), value: true},
                    {label: __('Disabled'), value: false},
                    {label: __('All'), value: 'all'}
                ]
            }
        },
        {
            title: __("Topology Discovery"),
            ftype: "list",
            listStore: {
                sorters: "label",
                data: [
                    {field_name: "enable_box_discovery_nri", label: __("NRI")},
                    {field_name: "enable_box_discovery_bfd", label: __("BFD")},
                    {field_name: "enable_box_discovery_cdp", label: __("CDP")},
                    {field_name: "enable_box_discovery_huawei_ndp", label: __("Huawei NDP")},
                    {field_name: "enable_box_discovery_mikrotik_ndp", label: __("MikroTik NDP")},
                    {field_name: "enable_box_discovery_fdp", label: __("FDP")},
                    {field_name: "enable_box_discovery_lldp", label: __("LLDP")},
                    {field_name: "enable_box_discovery_oam", label: __("OAM")},
                    {field_name: "enable_box_discovery_rep", label: __("REP")},
                    {field_name: "enable_box_discovery_stp", label: __("STP")},
                    {field_name: "enable_box_discovery_udld", label: __("UDLD")},
                    {field_name: "enable_box_discovery_lacp", label: __("LACP")}
                ]
            },
            valuesStore: {
                sorters: "label",
                data: [
                    {label: __('Enabled'), value: true},
                    {label: __('Disabled'), value: false},
                    {label: __('All'), value: 'all'}
                ]
            }
        },
        {
            title: __("Periodic Discovery"),
            ftype: "list",
            listStore: {
                sorters: "label",
                data: [
                    {field_name: "enable_periodic_discovery_uptime", label: __("Uptime")},
                    {field_name: "enable_periodic_discovery_interface_status", label: __("Interface status")},
                    {field_name: "enable_periodic_discovery_mac", label: __("MAC")},
                    {field_name: "enable_periodic_discovery_metrics", label: __("Metrics")}
                ]
            },
            valuesStore: {
                sorters: "label",
                data: [
                    {label: __('Enabled'), value: true},
                    {label: __('Disabled'), value: false},
                    {label: __('All'), value: 'all'}
                ]
            }
        }
    ],
    //
    onValidationSettings: function() {
        var me = this;
        me.showItem(me.ITEM_VALIDATION_SETTINGS).preview(me.currentRecord);
    }
});
