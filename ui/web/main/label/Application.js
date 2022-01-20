//---------------------------------------------------------------------
// main.label application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.label.Application");

Ext.define("NOC.main.label.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.label.Model",
        "NOC.main.remotesystem.LookupField",
        "Ext.ux.form.ColorField",
        "Ext.ux.form.GridField"
    ],
    model: "NOC.main.label.Model",
    search: true,
    viewModel: {
        data: {
            is_builtin: false,
            is_regex: false,
            is_scoped: false,
            is_wildcard: false,
        },
        formulas: {
            isEnableDisable: function(get) {
                return get("is_builtin");
            },
            isEnableDisableRx: function(get) {
                return get("is_builtin") || get("is_wildcard");
            },
        }
    },
    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Label"),
                    dataIndex: "name",
                    width: 300,
                    renderer: function(v, _x, item) {
                        return NOC.render.Label({
                            badges: item.data.badges,
                            name: item.data.name,
                            description: item.data.description || "",
                            bg_color1: item.data.bg_color1 || 0,
                            fg_color1: item.data.fg_color1 || 0,
                            bg_color2: item.data.bg_color2 || 0,
                            fg_color2: item.data.fg_color2 || 0
                        });
                    }
                },
                {
                    text: __("Protected"),
                    dataIndex: "is_protected",
                    width: 50,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("Allow"),
                    dataIndex: "enable_agent",
                    flex: 1,
                    renderer: function(_x, _y, item) {
                        let r = [];
                        if(item.data.enable_agent) {
                            r.push(__("Agent"));
                        }
                        if(item.data.enable_service) {
                            r.push(__("Service"));
                        }
                        if(item.data.enable_serviceprofile) {
                            r.push(__("Service Profile"));
                        }
                        if(item.data.enable_managedobject) {
                            r.push(__("Managed Object"));
                        }
                        if(item.data.enable_managedobjectprofile) {
                            r.push(__("Managed Object Profile"));
                        }
                        if(item.data.enable_administrativedomain) {
                            r.push(__("Administrative Domain"));
                        }
                        if(item.data.enable_authprofile) {
                            r.push(__("Auth Profile"));
                        }
                        if(item.data.enable_commandsnippet) {
                            r.push(__("Command Snippet"));
                        }
                        if(item.data.enable_allocationgroup) {
                            r.push(__("Allocation Group"));
                        }
                        if(item.data.enable_networksegment) {
                            r.push(__("Network Segment"));
                        }
                        if(item.data.enable_object) {
                            r.push(__("Object"));
                        }
                        if(item.data.enable_objectmodel) {
                            r.push(__("Object Model"));
                        }
                        if(item.data.enable_platform) {
                            r.push(__("Platfrom"));
                        }
                        if(item.data.enable_resourcegroup) {
                            r.push(__("Resource Group"));
                        }
                        if(item.data.enable_sensorprofile) {
                            r.push(__("Sensor Profile"));
                        }
                        if(item.data.enable_sensor) {
                            r.push(__("Sensor"));
                        }
                        if(item.data.enable_interface) {
                            r.push(__("Interface"));
                        }
                        if(item.data.enable_subscriber) {
                            r.push(__("Subscriber"));
                        }
                        if(item.data.enable_subscriberprofile) {
                            r.push(__("Subscriber Profile"));
                        }
                        if(item.data.enable_supplier) {
                            r.push(__("Supplier"));
                        }
                        if(item.data.enable_supplierprofile) {
                            r.push(__("Supplier Profile"));
                        }
                        if(item.data.enable_dnszone) {
                            r.push(__("DNS Zone"));
                        }
                        if(item.data.enable_dnszonerecord) {
                            r.push(__("DNS Zone Record"));
                        }
                        if(item.data.enable_division) {
                            r.push(__("GIS Division"));
                        }
                        if(item.data.enable_kbentry) {
                            r.push(__("KB Entry"));
                        }
                        if(item.data.enable_ipaddress) {
                            r.push(__("IP Address"));
                        }
                        if(item.data.enable_addressprofile) {
                            r.push(__("IP Address Profile"));
                        }
                        if(item.data.enable_ipaddressrange) {
                            r.push(__("IP Address Range"));
                        }
                        if(item.data.enable_ipprefix) {
                            r.push(__("IP Prefix"));
                        }
                        if(item.data.enable_prefixprofile) {
                            r.push(__("Prefix Profile"));
                        }
                        if(item.data.enable_vrf) {
                            r.push(__("VRF"));
                        }
                        if(item.data.enable_vrfgroup) {
                            r.push(__("VRF Group"));
                        }
                        if(item.data.enable_asn) {
                            r.push(__("AS"));
                        }
                        if(item.data.enable_assetpeer) {
                            r.push(__("Asset Peer"));
                        }
                        if(item.data.enable_peer) {
                            r.push(__("Peer"));
                        }
                        if(item.data.enable_vc) {
                            r.push(__("VC"));
                        }
                        if(item.data.enable_vlan) {
                            r.push(__("VLAN"));
                        }
                        if(item.data.enable_vlanprofile) {
                            r.push(__("VLAN Profile"));
                        }
                        if(item.data.enable_vpn) {
                            r.push(__("VPN"));
                        }
                        if(item.data.enable_vpnprofile) {
                            r.push(__("VPN Profile"));
                        }
                        if(item.data.enable_slaprobe) {
                            r.push(__("SLA Probe"));
                        }
                        if(item.data.enable_slaprofile) {
                            r.push(__("SLA Profile"));
                        }
                        if(item.data.enable_workflowstate) {
                            r.push(__("Workflow State"));
                        }
                        if(item.data.enable_firmwarepolicy) {
                            r.push(__("Firmware Policy"));
                        }
                        return r.join(", ");
                    }
                },
                {
                    text: __("Expose"),
                    dataIndex: "expose_metric",
                    flex: 1,
                    renderer: function(_x, _y, item) {
                        let r = [];
                        if(item.data.expose_metric) {
                            r.push(__("Metric"));
                        }
                        if(item.data.expose_datastream) {
                            r.push(__("Datastream"));
                        }
                        if(item.data.expose_alarm) {
                            r.push(__("Alarm"));
                        }
                        return r.join(", ");
                    }
                }
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Label"),
                    uiStyle: "medium",
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "is_protected",
                    xtype: "checkbox",
                    boxLabel: __("Protected"),
                    allowBlank: true
                },
                {
                    name: "propagate",
                    xtype: "checkbox",
                    boxLabel: __("Propagate"),
                    allowBlank: true,
                    bind: {
                        disabled: "{!is_wildcard}"
                    },
                },
                {
                    name: "is_wildcard",
                    xtype: "checkbox",
                    bind: {
                        value: "{is_wildcard}"
                    },
                    boxLabel: __("Wildcard"),
                    hidden: true
                },
                {
                    name: "is_autogenerated",
                    xtype: "checkbox",
                    boxLabel: __("Autogenerated"),
                    disabled: true
                },
                {
                    name: "is_builtin",
                    xtype: "checkbox",
                    boxLabel: __("Is Builtin"),
                    disabled: true,
                    bind: {
                        value: "{is_builtin}"
                    },
                },
                {
                    name: "is_regex",
                    xtype: "checkbox",
                    bind: {
                        value: "{is_regex}",
                        disabled: "{isEnableDisableRx}"
                    },
                    boxLabel: __("Regexp Label"),
                },
                {
                    name: "match_regex",
                    xtype: "gridfield",
                    fieldLabel: __("Regex Label"),
                    bind: {
                        disabled: "{!is_regex}"
                    },
                    columns: [
                        {
                            text: __("REGEX"),
                            dataIndex: "regexp",
                            width: 300,
                            editor: "textfield",
                            allowBlank: false
                        },
                        {
                            text: __("Multiline"),
                            dataIndex: "flag_multiline",
                            width: 50,
                            checked: false,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        },
                        {
                            text: __("DotALL"),
                            dataIndex: "flag_dotall",
                            width: 50,
                            checked: false,
                            renderer: NOC.render.Bool,
                            editor: "checkbox"
                        },
                        {
                            text: __("Regex Scope"),
                            dataIndex: "scope",
                            width: 200,
                            allowBlank: false,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["managedobject_name", __("Managed Object Name")],
                                    ["managedobject_address", __("Managed Object Address")],
                                    ["managedobject_description", __("Managed Object Description")],
                                    ["interface_name", __("Interface Name")],
                                    ["interface_description", __("Interface Description")],
                                    ["sensor_local_id", __("Sensor Local ID")]
                                ]
                            },
                            renderer: NOC.render.Choices({
                                "managedobject_name": __("Managed Object Name"),
                                "managedobject_address": __("Managed Object Address"),
                                "managedobject_description": __("Managed Object Description"),
                                "interface_name": __("Interface Name"),
                                "interface_description": __("Interface Description"),
                                "sensor_local_id": __("Sensor Local ID")
                            })
                        },
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Colors"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "bg_color1",
                            xtype: "colorfield",
                            fieldLabel: __("Background"),
                            allowBlank: false,
                            uiStyle: "medium"
                        },
                        {
                            name: "fg_color1",
                            xtype: "colorfield",
                            fieldLabel: __("Foreground"),
                            allowBlank: false,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Scoped Value Colors"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "bg_color2",
                            xtype: "colorfield",
                            fieldLabel: __("Background"),
                            allowBlank: false,
                            uiStyle: "medium"
                        },
                        {
                            name: "fg_color2",
                            xtype: "colorfield",
                            fieldLabel: __("Foreground"),
                            allowBlank: false,
                            uiStyle: "medium"
                        }
                    ]
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
                    xtype: "fieldset",
                    layout: "vbox",
                    title: __("Enable"),
                    bind: {
                        disabled: "{isEnableDisable}"
                    },
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            xtype: "fieldset",
                            layout: "hbox",
                            title: __("ManagedObject"),
                            defaults: {
                                padding: 4,
                                labelAlign: "right"
                            },
                            items: [
                                {
                                    name: "enable_managedobject",
                                    xtype: "checkbox",
                                    boxLabel: __("Managed Object")
                                },
                                {
                                    name: "enable_managedobjectprofile",
                                    xtype: "checkbox",
                                    boxLabel: __("Managed Object Profile"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_agent",
                                    xtype: "checkbox",
                                    boxLabel: __("Agent"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_firmwarepolicy",
                                    xtype: "checkbox",
                                    boxLabel: __("Firmware Policy"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_service",
                                    xtype: "checkbox",
                                    boxLabel: __("Service"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_serviceprofile",
                                    xtype: "checkbox",
                                    boxLabel: __("Service Profile"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_slaprobe",
                                    xtype: "checkbox",
                                    boxLabel: __("SLA Probe"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_slaprofile",
                                    xtype: "checkbox",
                                    boxLabel: __("SLA Profile"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_interface",
                                    xtype: "checkbox",
                                    boxLabel: __("Interface")
                                },
                                {
                                    name: "enable_alarm",
                                    xtype: "checkbox",
                                    boxLabel: __("Alarm")
                                }
                            ]
                        },
                        {
                            xtype: "fieldset",
                            layout: "hbox",
                            title: __("IP / DNS"),
                            defaults: {
                                padding: 4,
                                labelAlign: "right"
                            },
                            bind: {
                                disabled: "{is_regex}"
                            },
                            items: [
                                {
                                    name: "enable_ipaddress",
                                    xtype: "checkbox",
                                    boxLabel: __("IP Address")
                                },
                                {
                                    name: "enable_addressprofile",
                                    xtype: "checkbox",
                                    boxLabel: __("IP Address Profile")
                                },
                                {
                                    name: "enable_ipaddressrange",
                                    xtype: "checkbox",
                                    boxLabel: __("IP Address Range")
                                },
                                {
                                    name: "enable_ipprefix",
                                    xtype: "checkbox",
                                    boxLabel: __("IP Prefix")
                                },
                                {
                                    name: "enable_prefixprofile",
                                    xtype: "checkbox",
                                    boxLabel: __("Prefix Profile")
                                },
                                {
                                    name: "enable_vrf",
                                    xtype: "checkbox",
                                    boxLabel: __("VRF")
                                },
                                {
                                    name: "enable_vrfgroup",
                                    xtype: "checkbox",
                                    boxLabel: __("VRF Group")
                                },
                                {
                                    name: "enable_asn",
                                    xtype: "checkbox",
                                    boxLabel: __("AS")
                                },
                                {
                                    name: "enable_assetpeer",
                                    xtype: "checkbox",
                                    boxLabel: __("Asset Peer")
                                },
                                {
                                    name: "enable_peer",
                                    xtype: "checkbox",
                                    boxLabel: __("Peer")
                                },
                                {
                                    name: "enable_dnszone",
                                    xtype: "checkbox",
                                    boxLabel: __("DNS Zone")
                                },
                                {
                                    name: "enable_dnszonerecord",
                                    xtype: "checkbox",
                                    boxLabel: __("DNS Zone")
                                },
                            ]
                        },
                        {
                            xtype: "fieldset",
                            layout: "hbox",
                            title: __("Inventory"),
                            defaults: {
                                padding: 4,
                                labelAlign: "right"
                            },
                            items: [
                                {
                                    name: "enable_allocationgroup",
                                    xtype: "checkbox",
                                    boxLabel: __("Allocation Group"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_networksegment",
                                    xtype: "checkbox",
                                    boxLabel: __("Network Segment"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_object",
                                    xtype: "checkbox",
                                    boxLabel: __("Object"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_objectmodel",
                                    xtype: "checkbox",
                                    boxLabel: __("Object Model"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_platform",
                                    xtype: "checkbox",
                                    boxLabel: __("Platform"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_resourcegroup",
                                    xtype: "checkbox",
                                    boxLabel: __("Resource Group"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_sensorprofile",
                                    xtype: "checkbox",
                                    boxLabel: __("Sensor Profile"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                                {
                                    name: "enable_sensor",
                                    xtype: "checkbox",
                                    boxLabel: __("Sensor")
                                },
                                {
                                    name: "enable_division",
                                    xtype: "checkbox",
                                    boxLabel: __("GIS Division"),
                                    bind: {
                                        disabled: "{is_regex}"
                                    }
                                },
                            ]
                        },
                        {
                            xtype: "fieldset",
                            layout: "hbox",
                            title: __("VC"),
                            defaults: {
                                padding: 4,
                                labelAlign: "right"
                            },
                            bind: {
                                disabled: "{is_regex}"
                            },
                            items: [
                                {
                                    name: "enable_vc",
                                    xtype: "checkbox",
                                    boxLabel: __("VC")
                                },
                                {
                                    name: "enable_vlan",
                                    xtype: "checkbox",
                                    boxLabel: __("VLAN")
                                },
                                {
                                    name: "enable_vlanprofile",
                                    xtype: "checkbox",
                                    boxLabel: __("VLAN Profile")
                                },
                                {
                                    name: "enable_vpn",
                                    xtype: "checkbox",
                                    boxLabel: __("VPN")
                                },
                                {
                                    name: "enable_vpnprofile",
                                    xtype: "checkbox",
                                    boxLabel: __("VPN Profile")
                                }
                            ]
                        },
                        {
                            xtype: "fieldset",
                            layout: "hbox",
                            title: __("Other"),
                            defaults: {
                                padding: 4,
                                labelAlign: "right"
                            },
                            bind: {
                                disabled: "{is_regex}"
                            },
                            items: [
                                {
                                    name: "enable_administrativedomain",
                                    xtype: "checkbox",
                                    boxLabel: __("Administrative Domain")
                                },
                                {
                                    name: "enable_authprofile",
                                    xtype: "checkbox",
                                    boxLabel: __("Auth Profile")
                                },
                                {
                                    name: "enable_commandsnippet",
                                    xtype: "checkbox",
                                    boxLabel: __("Command Snippet")
                                },
                                {
                                    name: "enable_subscriber",
                                    xtype: "checkbox",
                                    boxLabel: __("Subscriber")
                                },
                                {
                                    name: "enable_subscriberprofile",
                                    xtype: "checkbox",
                                    boxLabel: __("Subscriber Profile")
                                },
                                {
                                    name: "enable_supplier",
                                    xtype: "checkbox",
                                    boxLabel: __("Supplier")
                                },
                                {
                                    name: "enable_supplierprofile",
                                    xtype: "checkbox",
                                    boxLabel: __("Supplier Profile")
                                },
                                {
                                    name: "enable_kbentry",
                                    xtype: "checkbox",
                                    boxLabel: __("KB Entry")
                                },
                                {
                                    name: "enable_workflowstate",
                                    xtype: "checkbox",
                                    boxLabel: __("Workflow State")
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Expose"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "expose_metric",
                            xtype: "checkbox",
                            boxLabel: __("Metrics")
                        },
                        {
                            name: "expose_datastream",
                            xtype: "checkbox",
                            boxLabel: __("Datastream")
                        },
                        {
                            name: "expose_alarm",
                            xtype: "checkbox",
                            boxLabel: __("Alarm")
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
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },
    filters: [
        {
            title: __("Manual"),
            name: "is_builtin_labels",
            ftype: "boolean"
        },
        {
            title: __("Regex"),
            name: "is_regex",
            ftype: "boolean"
        },
        {
            title: __("Match"),
            name: "is_matched",
            ftype: "boolean"
        }
    ],
});
