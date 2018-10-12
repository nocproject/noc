//---------------------------------------------------------------------
// sa.managedobjectprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
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
        "NOC.main.ref.windowfunction.LookupField",
        "Ext.ux.form.MultiIntervalField",
        "NOC.pm.metrictype.LookupField",
        "NOC.pm.thresholdprofile.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.ip.prefixprofile.LookupField",
        "NOC.ip.addressprofile.LookupField",
        "NOC.vc.vpnprofile.LookupField",
        "NOC.main.template.LookupField",
        "NOC.main.extstorage.LookupField",
        "NOC.main.handler.LookupField"
    ],
    model: "NOC.sa.managedobjectprofile.Model",
    search: true,
    helpId: "reference-managed-object-profile",
    rowClassField: "row_class",
    validationModelId: "sa.ManagedObjectProfile",
    viewModel: {
        data: {
            enableBoxDiscoveryConfig: false,
            enableBoxDiscoveryVPNInterface: false,
            enableBoxDiscoveryVPNMPLS: false,
            enableBoxDiscoveryPrefixInterface: false,
            enableBoxDiscoveryPrefixNeighbor: false,
            enableBoxDiscoveryAddressInterface: false,
            enableBoxDiscoveryAddressManagement: false,
            enableBoxDiscoveryAddressDHCP: false,
            enableBoxDiscoveryAddressNeighbor: false,
            enableBoxDiscoveryHK: false,
            enableBoxDiscoveryNRIPortmap: false,
            enableBoxDiscoveryCPEStatus: false
        },
        formulas: {
            disableConfigPolicy: {
                bind: {
                    bindTo: '{mirrorPolicy.selection}',
                    deep: true
                },
                get: function(record) {
                    return record ? this.data.enableBoxDiscoveryConfig.checked
                        && record.get('id') === 'D' : true;
                }
            },
            disableBeefPolicy: {
                bind: {
                    bindTo: '{beefPolicy.selection}',
                    deep: true
                },
                get: function(record) {
                    return record ? record.get('id') === 'D' : true;
                }
            }
        }
    },

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
                    tabPosition: "left",
                    tabBar: {
                        tabRotation: 0,
                        layout: {
                            align: "stretch"
                        }
                    },
                    anchor: "-0, -50",
                    defaults: {
                        autoScroll: true,
                        layout: "anchor",
                        textAlign: "left",
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
                                },
                                {
                                    name: "fqdn_suffix",
                                    xtype: "textfield",
                                    fieldLabel: __("FQDN Suffix"),
                                    allowBlank: true,
                                    uiStyle: "large"
                                },
                                {
                                    name: "address_resolution_policy",
                                    xtype: "combobox",
                                    fieldLabel: __("Address Resolution Policy"),
                                    store: [
                                        ["D", __("Disabled")],
                                        ["O", __("Once")],
                                        ["E", __("Enabled")]
                                    ],
                                    allowBlank: false,
                                    uiStyle: "medium"
                                },
                                {
                                    name: "resolver_handler",
                                    xtype: "main.handler.LookupField",
                                    fieldLabel: __("Resolver Handler"),
                                    allowBlank: true,
                                    uiStyle: "medium",
                                    query: {
                                        allow_resolver: true
                                    }
                                }
                            ]
                        },
                        {
                            title: __("Access"),
                            tooltip: __("Worked with devices settings"),
                            items: [
                                {
                                    name: "access_preference",
                                    xtype: "combobox",
                                    tooltip: __("Protocol priority worked on device. <br/>" +
                                        "Warning! Device profile (SA Profile) should support worked in selected mode"),
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
                                    value: "CS",
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "cli_session_policy",
                                    xtype: "combobox",
                                    tooltip: __("Use one session worked on device. <br/>" +
                                        "If disabled - worked one script - one login. Logout after script end."),
                                    fieldLabel: __("CLI Session Policy"),
                                    labelWidth: 220,
                                    allowBlank: true,
                                    labelAlign: "left",
                                    uiStyle: "medium",
                                    store: [
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    value: "E",
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "cli_privilege_policy",
                                    xtype: "combobox",
                                    tooltip: __("Do enable if login unprivilege mode on device. <br/>" +
                                        "Raise Privileges - send enable, Do not raise - work on current mode <br/>" +
                                        "(immediately after login)"),
                                    fieldLabel: __("CLI Privilege Policy"),
                                    labelWidth: 220,
                                    allowBlank: true,
                                    uiStyle: "medium",
                                    store: [
                                        ["D", __("Do not raise")],
                                        ["E", __("Raise Privileges")]
                                    ],
                                    value: "E",
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                }
                            ],
                            listeners: {
                                render: me.addTooltip
                            }
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
                                },
                                {
                                    name: "syslog_archive_policy",
                                    xtype: "combobox",
                                    labelWidth: 150,
                                    fieldLabel: __("Syslog Archive Policy"),
                                    store: [
                                        ["E", __("Enable")],
                                        ["D", __("Disable")]
                                    ],
                                    value: "D",
                                    allowBlank: false,
                                    uiStyle: "medium"
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
                                            name: "enable_box_discovery_id",
                                            xtype: "checkboxfield",
                                            boxLabel: __("ID")
                                        },
                                        {
                                            name: "enable_box_discovery_config",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Config"),
                                            reference: "enableBoxDiscoveryConfig"
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
                                            name: "enable_box_discovery_cpestatus",
                                            xtype: "checkboxfield",
                                            boxLabel: __("CPE status"),
                                            reference: "enableBoxDiscoveryCPEStatus"
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
                                                    boxLabel: __("NRI"),
                                                    bind: {
                                                        disabled: "{!enableBoxDiscoveryNRIPortmap.checked}"
                                                    }
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
                                    title: __("IPAM (VPN)"),
                                    layout: {
                                        type: "table",
                                        columns: 3
                                    },
                                    defaults: {
                                        padding: "2px 4px 2px 4px"
                                    },
                                    items: [
                                        {
                                            xtype: "label",
                                            text: __("Type")
                                        },
                                        {
                                            xtype: "label",
                                            text: __("Enable")
                                        },
                                        {
                                            xtype: "label",
                                            text: __("VPN Profile")
                                        },
                                        {
                                            xtype: "label",
                                            text: __("Interface")
                                        },
                                        {
                                            name: "enable_box_discovery_vpn_interface",
                                            xtype: "checkbox",
                                            reference: "enableBoxDiscoveryVPNInterface"
                                        },
                                        {
                                            name: "vpn_profile_interface",
                                            xtype: "vc.vpnprofile.LookupField",
                                            allowBlank: true,
                                            bind: {
                                                disabled: "{!enableBoxDiscoveryVPNInterface.checked}"
                                            }
                                        },
                                        {
                                            xtype: "label",
                                            text: __("MPLS")
                                        },
                                        {
                                            name: "enable_box_discovery_vpn_mpls",
                                            xtype: "checkbox",
                                            reference: "enableBoxDiscoveryVPNMPLS"
                                        },
                                        {
                                            name: "vpn_profile_mpls",
                                            xtype: "vc.vpnprofile.LookupField",
                                            allowBlank: true,
                                            bind: {
                                                disabled: "{!enableBoxDiscoveryVPNMPLS.checked}"
                                            }
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("IPAM (Prefix)"),
                                    layout: {
                                        type: "table",
                                        columns: 3
                                    },
                                    defaults: {
                                        padding: "2px 4px 2px 4px"
                                    },
                                    items: [
                                        {
                                            xtype: "label",
                                            text: __("Type")
                                        },
                                        {
                                            xtype: "label",
                                            text: __("Enable")
                                        },
                                        {
                                            xtype: "label",
                                            text: __("Prefix Profile")
                                        },
                                        {
                                            xtype: "label",
                                            text: __("Interface")
                                        },
                                        {
                                            name: "enable_box_discovery_prefix_interface",
                                            xtype: "checkbox",
                                            reference: "enableBoxDiscoveryPrefixInterface"
                                        },
                                        {
                                            name: "prefix_profile_interface",
                                            xtype: "ip.prefixprofile.LookupField",
                                            allowBlank: true,
                                            bind: {
                                                disabled: "{!enableBoxDiscoveryPrefixInterface.checked}"
                                            }
                                        },
                                        {
                                            xtype: "label",
                                            text: __("Neighbor")
                                        },
                                        {
                                            name: "enable_box_discovery_prefix_neighbor",
                                            xtype: "checkbox",
                                            reference: "enableBoxDiscoveryPrefixNeighbor"
                                        },
                                        {
                                            name: "prefix_profile_neighbor",
                                            xtype: "ip.prefixprofile.LookupField",
                                            allowBlank: true,
                                            bind: {
                                                disabled: "{!enableBoxDiscoveryPrefixNeighbor.checked}"
                                            }

                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("IPAM (Address)"),
                                    layout: {
                                        type: "table",
                                        columns: 3
                                    },
                                    defaults: {
                                        padding: "2px 4px 2px 4px"
                                    },
                                    items: [
                                        {
                                            xtype: "label",
                                            text: __("Type")
                                        },
                                        {
                                            xtype: "label",
                                            text: __("Enable")
                                        },
                                        {
                                            xtype: "label",
                                            text: __("Address Profile")
                                        },
                                        {
                                            xtype: "label",
                                            text: __("Interface")
                                        },
                                        {
                                            name: "enable_box_discovery_address_interface",
                                            xtype: "checkbox",
                                            reference: "enableBoxDiscoveryAddressInterface"
                                        },
                                        {
                                            name: "address_profile_interface",
                                            xtype: "ip.addressprofile.LookupField",
                                            allowBlank: true,
                                            bind: {
                                                disabled: "{!enableBoxDiscoveryAddressInterface.checked}"
                                            }
                                        },
                                        {
                                            xtype: "label",
                                            text: __("Management")
                                        },
                                        {
                                            name: "enable_box_discovery_address_management",
                                            xtype: "checkbox",
                                            reference: "enableBoxDiscoveryAddressManagement"
                                        },
                                        {
                                            name: "address_profile_management",
                                            xtype: "ip.addressprofile.LookupField",
                                            allowBlank: true,
                                            bind: {
                                                disabled: "{!enableBoxDiscoveryAddressManagement.checked}"
                                            }
                                        },
                                        {
                                            xtype: "label",
                                            text: __("DHCP")
                                        },
                                        {
                                            name: "enable_box_discovery_address_dhcp",
                                            xtype: "checkbox",
                                            reference: "enableBoxDiscoveryAddressDHCP"
                                        },
                                        {
                                            name: "address_profile_dhcp",
                                            xtype: "ip.addressprofile.LookupField",
                                            allowBlank: true,
                                            bind: {
                                                disabled: "{!enableBoxDiscoveryAddressDHCP.checked}"
                                            }
                                        },
                                        {
                                            xtype: "label",
                                            text: __("Neighbor")
                                        },
                                        {
                                            name: "enable_box_discovery_address_neighbor",
                                            xtype: "checkbox",
                                            reference: "enableBoxDiscoveryAddressNeighbor"
                                        },
                                        {
                                            name: "address_profile_neighbor",
                                            xtype: "ip.addressprofile.LookupField",
                                            allowBlank: true,
                                            bind: {
                                                disabled: "{!enableBoxDiscoveryAddressNeighbor.checked}"
                                            }
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
                                    title: __("CPE Status"),
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
                                                    name: "box_discovery_cpestatus_policy",
                                                    xtype: "combobox",
                                                    fieldLabel: __("Box CPE Status Policy"),
                                                    labelWidth: 120,
                                                    allowBlank: true,
                                                    tooltip: __('Set Policy for CPE Status Discovery. ' +
                                                        'S - Check only CPE Statuses (script get_cpe_status)' +
                                                        'F - Check ALL CPE info (script get_cpe)'),
                                                    displayField: "label",
                                                    valueField: "id",
                                                    store: {
                                                        fields: ["id", "label"],
                                                        data: [
                                                            {"id": "S", "label": __("Status only")},
                                                            {"id": "F", "label": __("Full")}
                                                        ]
                                                    },
                                                    bind: {
                                                        disabled: "{!enableBoxDiscoveryCPEStatus.checked}"
                                                    },
                                                    listeners: {
                                                        render: me.addTooltip
                                                    }
                                                }
                                            ]
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
                                    title: __("NRI"),
                                    layouy: "hbox",
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            name: "enable_box_discovery_nri_portmap",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Portmapper"),
                                            reference: "enableBoxDiscoveryNRIPortmap"
                                        },
                                        {
                                            name: "enable_box_discovery_nri_service",
                                            xtype: "checkboxfield",
                                            boxLabel: __("Service Binding"),
                                            bind: {
                                                disabled: "{!enableBoxDiscoveryNRIPortmap.checked}"
                                            }
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
                                            boxLabel: __("Housekeeping"),
                                            reference: "enableBoxDiscoveryHK"
                                        },
                                        {
                                            name: "hk_handler",
                                            xtype: "textfield",
                                            labelAlign: "left",
                                            fieldLabel: __("Handler"),
                                            allowBlank: true,
                                            bind: {
                                                disabled: "{!enableBoxDiscoveryHK.checked}"
                                            }
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
                                        columns: 5
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
                                            name: "enable_periodic_discovery_cpestatus",
                                            xtype: "checkboxfield",
                                            boxLabel: __("CPE status"),
                                            reference: "enablePeriodicDiscoveryCPEStatus"
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
                                    title: __("Periodic CPE Status"),
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
                                                    name: "periodic_discovery_cpestatus_policy",
                                                    xtype: "combobox",
                                                    fieldLabel: __("Periodic CPE Status Policy"),
                                                    labelWidth: 150,
                                                    allowBlank: true,
                                                    tooltip: __('Set Policy for CPE Status Discovery. ' +
                                                        'S - Check only CPE Statuses (script get_cpe_status)' +
                                                        'F - Check ALL CPE info (script get_cpe)'),
                                                    displayField: "label",
                                                    valueField: "id",
                                                    store: {
                                                        fields: ["id", "label"],
                                                        data: [
                                                            {"id": "S", "label": __("Status only")},
                                                            {"id": "F", "label": __("Full")}
                                                        ]
                                                    },
                                                    bind: {
                                                        disabled: "{!enablePeriodicDiscoveryCPEStatus.checked}"
                                                    },
                                                    listeners: {
                                                        render: me.addTooltip
                                                    }
                                                }
                                            ]
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
                            title: __("Config"),
                            tooltip: __("Settings policy for config discovery: Validation and mirroring config"),
                            items: [
                                {
                                    xtype: "fieldset",
                                    title: __("Config Mirror"),
                                    layout: "hbox",
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            name: "config_mirror_policy",
                                            xtype: "combobox",
                                            reference: "mirrorPolicy",
                                            fieldLabel: __("Mirror Policy"),
                                            allowBlank: false,
                                            tooltip: __('Mirror collected config after Config discovery. <br/>' +
                                                'Always Mirror - mirror every discovery run <br/>' +
                                                'Mirror on Change - save only if detect config changed'),
                                            displayField: "label",
                                            valueField: "id",
                                            store: {
                                                fields: ["id", "label"],
                                                data: [
                                                    {"id": "D", "label": __("Disabled")},
                                                    {"id": "A", "label": __("Always Mirror")},
                                                    {"id": "C", "label": __("Mirror on Change")}
                                                ]
                                            },
                                            bind: {
                                                disabled: "{!enableBoxDiscoveryConfig.checked}"
                                            },
                                            listeners: {
                                                render: me.addTooltip
                                            }

                                        },
                                        {
                                            name: "config_mirror_storage",
                                            xtype: "main.extstorage.LookupField",
                                            fieldLabel: __("Storage"),
                                            query: {
                                                type: "config_mirror"
                                            },
                                            allowBlank: true,
                                            tooltip: __('External storage for config save. ' +
                                                'Setup in Main -> Setup -> Ext. storage'),
                                            bind: {
                                                disabled: "{disableConfigPolicy}"
                                            },
                                            listeners: {
                                                render: me.addTooltip
                                            }
                                        },
                                        {
                                            name: "config_mirror_template",
                                            xtype: "main.template.LookupField",
                                            fieldLabel: __("Path Template"),
                                            allowBlank: true,
                                            tooltip: __('Save config path template. ' +
                                                'Setup on Main -> Setup -> Templates, subject form.' +
                                                'Simple is: {{ object.name }}.txt on subject or <br/>' +
                                                '{{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}} for time'),
                                            bind: {
                                                disabled: "{disableConfigPolicy}"
                                            },
                                            listeners: {
                                                render: me.addTooltip
                                            }
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("Config Validation"),
                                    layout: "hbox",
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            name: "config_validation_policy",
                                            xtype: "combobox",
                                            fieldLabel: __("Validation Policy"),
                                            allowBlank: false,
                                            store: [
                                                ["D", __("Disabled")],
                                                ["A", __("Always Validate")],
                                                ["C", __("Validate on Change")]
                                            ],
                                            tooltip: __('Run config validate proccess: <br/>' +
                                                'Always Validate - every discovery run<br/>' +
                                                'Validate on Change - only if detect config changed'),
                                            bind: {
                                                disabled: "{!enableBoxDiscoveryConfig.checked}"
                                            },
                                            listeners: {
                                                render: me.addTooltip
                                            }
                                        }
                                    ]
                                },
                                {
                                    xtype: "fieldset",
                                    title: __("Beef"),
                                    layout: "hbox",
                                    defaults: {
                                        labelAlign: "top",
                                        padding: 4
                                    },
                                    items: [
                                        {
                                            name: "beef_policy",
                                            xtype: "combobox",
                                            reference: "beefPolicy",
                                            fieldLabel: __("Beef Policy"),
                                            allowBlank: false,
                                            displayField: "label",
                                            valueField: "id",
                                            store: {
                                                fields: ["id", "label"],
                                                data: [
                                                    {"id": "D", "label": __("Disabled")},
                                                    {"id": "A", "label": __("Always Collect")},
                                                    {"id": "C", "label": __("Collect on Change")}
                                                ]
                                            }
                                        },
                                        {
                                            name: "beef_storage",
                                            xtype: "main.extstorage.LookupField",
                                            fieldLabel: __("Storage"),
                                            query: {
                                                type: "beef"
                                            },
                                            allowBlank: true,
                                            bind: {
                                                disabled: "{disableBeefPolicy}"
                                            }
                                        },
                                        {
                                            name: "beef_path_template",
                                            xtype: "main.template.LookupField",
                                            fieldLabel: __("Path Template"),
                                            allowBlank: true,
                                            bind: {
                                                disabled: "{disableBeefPolicy}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            listeners: {
                                render: me.addTooltip
                            }
                        },
                        {
                            title: __("Metrics"),
                            tooltip: __("Setup colleced metric on divices (not Interface!). <br/>" +
                                "(Interface Metrics settings Inventory -> Setup -> Interface Profile)"),
                            items: [
                                {
                                    name: "metrics",
                                    xtype: "gridfield",
                                    fieldLabel: __("Metrics"),
                                    labelAlign: "top",
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
                                                xtype: "main.ref.windowfunction.LookupField"
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
                                        },
                                        {
                                            text: __("Profile"),
                                            dataIndex: "threshold_profile",
                                            width: 150,
                                            editor: {
                                                xtype: "pm.thresholdprofile.LookupField"
                                            },
                                            renderer: NOC.render.Lookup("threshold_profile")
                                        }
                                    ]

                                }
                            ],
                            listeners: {
                                render: me.addTooltip
                            }
                        },
                        {
                            title: __("MAC"),
                            tooltip: __("Filter settings for MAC disocovery"),
                            items: [
                                {
                                    name: "mac_collect_all",
                                    xtype: "checkbox",
                                    tooltip: __("Not filter collected MACs"),
                                    boxLabel: __("Collect All"),
                                    allowBlank: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "mac_collect_interface_profile",
                                    xtype: "checkbox",
                                    tooltip: __("Collect MACs only for allowed interfaces. <br/>" +
                                        "(MAC Discovery Policy on Inventory -> Setup -> Interface Profile)"),
                                    boxLabel: __("Collect if permitted by interface profile"),
                                    allowBlank: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "mac_collect_management",
                                    xtype: "checkbox",
                                    tooltip: __("Collect MAC only for managed VLAN. <br/>" +
                                        "Managed VLAN set in Inventory -> Setup -> NetworkSegmentProfile"),
                                    boxLabel: __("Collect from management VLAN"),
                                    allowBlank: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "mac_collect_multicast",
                                    xtype: "checkbox",
                                    tooltip: __("Collect MAC only for Multicast VLAN. <br/>" +
                                        "Multicast VLAN set in Inventory -> Setup -> NetworkSegmentProfile"),
                                    boxLabel: __("Collect from multicast VLAN"),
                                    allowBlank: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "mac_collect_vcfilter",
                                    xtype: "checkbox",
                                    tooltip: __("Collect MAC only for VLAN on VCFilter. <br/>" +
                                        "MVCFilter set in VC Management -> Setup -> VCFilter"),
                                    boxLabel: __("Collect from VLAN matching VC Filter"),
                                    allowBlank: true,
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                }
                            ],
                            listeners: {
                                render: me.addTooltip
                            }
                        },
                        {
                            title: __("Autosegmentation"),
                            tooltip: __("Settings for autosegmentatin proccess: <br/>" +
                                "Automaticaly detect segment for ManagedObject with this ObjectProfile.<br/>" +
                                "Uses MAC and needed MAC enable in Box"),
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
                                    tooltip: __("Max level (Common -> Level) there will be changed segment. <br/>" +
                                        "(Autosegmentation not worked with ManagedObject less this level"),
                                    labelWidth: 150,
                                    fieldLabel: __("Level Limit"),
                                    allowBlank: false,
                                    uiStyle: "small",
                                    listeners: {
                                        render: me.addTooltip
                                }
                                },
                                {
                                    name: "autosegmentation_segment_name",
                                    xtype: "textfield",
                                    tooltip: __("Jinja template for creating segment name. <br/>" +
                                        "Worked with \"Segmentate for object's segment\" and " +
                                        "\"Segmentate for child segment\" options"),
                                    tooltip: __(""),
                                    labelWidth: 150,
                                    fieldLabel: __("Segment Name"),
                                    allowBlank: true,
                                    uiStyle: "extra",
                                    listeners: {
                                        render: me.addTooltip
                                }
                                }
                            ],
                            listeners: {
                                render: me.addTooltip
                            }
                        },
                        {
                            title: __("Integration"),
                            tooltip: __("Field on this use in ETL proccess (sync on external system). <br/>" +
                                "Do not Edit field directly!"),
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
                            ],
                            listeners: {
                                render: me.addTooltip
                            }
                        },
                        {
                            title: __("Escalation"),
                            tooltip: __("Policy for do managedobject in escalation proccess: " +
                                "FM -> Setup -> Escalation"),
                            items: [
                                {
                                    name: "escalation_policy",
                                    xtype: "combobox",
                                    tooltip: __("Enable - allow escalate alarm for ManagedObject. <br/>" +
                                        "As Depended - allow escalate ManagedObject only as depend (not root) on alarm"),
                                    labelWidth: 150,
                                    fieldLabel: __("Escalation Policy"),
                                    allowBlank: true,
                                    uiStyle: "medium",
                                    store: [
                                        ["E", __("Enable")],
                                        ["D", __("Disable")],
                                        ["R", __("As Depended")]
                                    ],
                                    value: "E",
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                }
                            ],
                            listeners: {
                                render: me.addTooltip
                            }
                        },
                        {
                            title: __("Telemetry"),
                            tooltip: __("Setting for saving discovery operation on ClickHouse telemetry table. <br/>" +
                                "Warning! Activate telemetry if you really know for it. <br/>" +
                                "Enable overhad about +25% CPU usage"),
                            items: [
                                {
                                    name: "box_discovery_telemetry_sample",
                                    xtype: "numberfield",
                                    tooltip: __("Sampling value for Box discovery. Interval from 0 to 1. <br/>" +
                                        "1 - all jobs will saved, 0 - Not collect telemetry, <br/>" +
                                        " 0,99 ... 0,1 - chance to save"),
                                    labelWidth: 150,
                                    fieldLabel: __("Box Sample"),
                                    allowBlank: false,
                                    uiStyle: "medium",
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                },
                                {
                                    name: "periodic_discovery_telemetry_sample",
                                    xtype: "numberfield",
                                    tooltip: __('Sampling value for Periodic discovery. Interval from 0 to 1. <br/>' +
                                        '1 - all jobs will saved, 0 - Not collect telemetry, ' +
                                        ' 0,99 ... 0,1 - chance to save'),
                                    labelWidth: 150,
                                    fieldLabel: __("Periodic Sample"),
                                    allowBlank: false,
                                    uiStyle: "medium",
                                    listeners: {
                                        render: me.addTooltip
                                    }
                                }
                            ],
                            listeners: {
                                render: me.addTooltip
                            }
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
    },
    //
    cleanData: function(v) {
        Ext.each(v.metrics, function(m) {
            if(m.low_error === "") {
                m.low_error = null;
            }
            if(m.low_warn === "") {
                m.low_warn = null;
            }
            if(m.high_warn === "") {
                m.high_warn = null;
            }
            if(m.high_error === "") {
                m.high_error = null;
            }
        });
    }
});
