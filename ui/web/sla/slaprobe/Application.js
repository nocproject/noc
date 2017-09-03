//---------------------------------------------------------------------
// sla.slaprobe application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sla.slaprobe.Application");

Ext.define("NOC.sla.slaprobe.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sla.slaprobe.Model",
        "NOC.sa.managedobject.LookupField",
        "NOC.sla.slaprofile.LookupField"
    ],
    model: "NOC.sla.slaprobe.Model",
    rowClassField: "row_class",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Managed Object"),
                    dataIndex: "managed_object",
                    width: 200,
                    renderer: NOC.render.Lookup("managed_object")
                },
                {
                    text: __("Group"),
                    dataIndex: "group",
                    width: 200
                },
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Type"),
                    dataIndex: "type",
                    width: 75
                },
                {
                    text: __("Target"),
                    dataIndex: "target",
                    width: 200
                },
                {
                    text: __("Profile"),
                    dataIndex: "profile",
                    width: 150,
                    renderer: NOC.render.Lookup("profile")
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    flex: 1
                },
                {
                    text: __("Tags"),
                    dataIndex: "tags",
                    renderer: NOC.render.Tags,
                    width: 100
                }
            ],

            fields: [
                {
                    name: "managed_object",
                    xtype: "sa.managedobject.LookupField",
                    fieldLabel: __("Managed Object"),
                    allowBlank: false
                },
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "group",
                    xtype: "textfield",
                    fieldLabel: __("Group"),
                    allowBlank: true,
                    uiStyle: "medium"
                },
                {
                    name: "type",
                    xtype: "combobox",
                    fieldLabel: __("Type"),
                    allowBlank: false,
                    uiStyle: "medium",
                    store: [
                        ["icmp-echo", "icmp-echo"],
                        ["path-jitter", "path-jitter"],
                        ["udp-echo", "udp-echo"],
                        ["http-get", "http-get"],
                        ["dns", "dns"],
                        ["ftp", "ftp"],
                        ["dhcp", "dhcp"],
                        ["owamp", "OWAMP"],
                        ["twamp", "TWAMP"]
                    ]
                },
                {
                    name: "target",
                    xtype: "textfield",
                    fieldLabel: __("Target"),
                    allowBlank: false
                },
                {
                    name: "profile",
                    xtype: "sla.slaprofile.LookupField",
                    fieldLabel: __("Profile"),
                    allowBlank: true
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "hw_timestamps",
                    xtype: "checkbox",
                    boxLabel: __("HW. Timestamps"),
                    allowBlank: true
                },
                {
                    name: "tags",
                    xtype: "tagsfield",
                    fieldLabel: __("Tags"),
                    allowBlank: true,
                    uiStyle: "extra"
                }
            ],
            openDashboard: {
                icon: NOC.glyph.line_chart,
                color: NOC.colors.line_chart,
                type: 'ipsla',
                tooltip: __('Show IPSLA Dashboard')
            }
        });
        me.callParent();
    }
});
