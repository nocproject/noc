//---------------------------------------------------------------------
// ip.prefix application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.prefix.Application");

Ext.define("NOC.ip.prefix.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.ip.prefix.Model",
        "NOC.ip.prefix.LookupField",
        "NOC.ip.prefixprofile.LookupField",
        "NOC.ip.vrf.LookupField",
        "NOC.peer.as.LookupField",
        "NOC.vc.vc.LookupField",
        "NOC.main.resourcestate.LookupField",
        "NOC.project.project.LookupField",
        "NOC.ip.prefix.LookupField"
    ],
    model: "NOC.ip.prefix.Model",
    search: true,
    rowClassField: "row_class",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("VRF"),
                    dataIndex: "vrf",
                    width: 150,
                    renderer: NOC.render.Lookup("vrf")
                },
                {
                    text: __("Prefix"),
                    dataIndex: "prefix",
                    width: 150
                },
                {
                    text: __("Profile"),
                    dataIndex: "profile",
                    width: 150,
                    renderer: NOC.render.Lookup("profile")
                }
            ],
            fields:
                [
                    {
                        name: "vrf",
                        xtype: "ip.vrf.LookupField",
                        fieldLabel: __("VRF"),
                        allowBlank: false
                    },
                    {
                        name: "prefix",
                        xtype: "textfield",
                        fieldLabel: __("Prefix"),
                        allowBlank: false
                    },
                    {
                        name: "description",
                        xtype: "textarea",
                        fieldLabel: __("Description"),
                        allowBlank: true
                    },
                    {
                        name: "profile",
                        xtype: "ip.prefixprofile.LookupField",
                        fieldLabel: __("Profile"),
                        allowBlank: false
                    },
                    {
                        name: "afi",
                        xtype: "displayfield",
                        fieldLabel: __("Address Family"),
                        allowBlank: true
                    },
                    {
                        name: "asn",
                        xtype: "peer.as.LookupField",
                        fieldLabel: __("AS"),
                        allowBlank: false
                    },
                    {
                        name: "vc",
                        xtype: "vc.vc.LookupField",
                        fieldLabel: __("VC"),
                        allowBlank: true
                    },
                    {
                        name: "tags",
                        xtype: "tagsfield",
                        fieldLabel: __("Tags"),
                        allowBlank: true
                    },
                    {
                        name: "tt",
                        xtype: "numberfield",
                        fieldLabel: __("TT"),
                        allowBlank: true
                    },
                    {
                        name: "state",
                        xtype: "main.resourcestate.LookupField",
                        fieldLabel: __("State"),
                        allowBlank: false
                    },
                    {
                        name: "allocated_till",
                        xtype: "datefield",
                        startDay: 1,
                        fieldLabel: __("Allocated till"),
                        allowBlank: true
                    },
                    {
                        name: "ipv6_transition",
                        xtype: "ip.prefix.LookupField",
                        fieldLabel: __("ipv6 transition"),
                        allowBlank: true
                    },
                    {
                        name: "project",
                        xtype: "project.project.LookupField",
                        fieldLabel: __("Project"),
                        allowBlank: true
                    }
                ]
        });
        me.callParent()
    },

    levelFilter: {
        icon: NOC.glyph.level_down,
        color: NOC.colors.level_down,
        filter: 'parent',
        tooltip: __('Parent filter')
    }
});
