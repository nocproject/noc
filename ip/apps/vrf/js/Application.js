//---------------------------------------------------------------------
// ip.vrf application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.vrf.Application");

Ext.define("NOC.ip.vrf.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.ip.vrf.Model",
        "NOC.ip.vrfgroup.LookupField",
        "NOC.main.style.LookupField",
        "NOC.core.TagsField"
    ],
    model: "NOC.ip.vrf.Model",
    search: true,
    columns: [
        {
            text: "Name",
            dataIndex: "name"
        },
        {
            text: "RD",
            dataIndex: "rd",
            width: 100
        },
        {
            text: "Group",
            dataIndex: "vrf_group",
            renderer: NOC.render.Lookup("vrf_group")
        },
        {
            text: "IPv4",
            dataIndex: "afi_ipv4",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "IPv6",
            dataIndex: "afi_ipv6",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "Description",
            dataIndex: "description",
            flex: 1
        },
        {
            text: "Tags",
            dataIndex: "tags",
            renderer: NOC.render.Tags
        }
    ],
    fields: [
        {
            name: "name",
            xtype: "textfield",
            fieldLabel: "VRF",
            allowBlank: false
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Is Active",
            allowBlank: false
        },
        {
            name: "vrf_group",
            xtype: "ip.vrfgroup.LookupField",
            fieldLabel: "VRF Group",
            allowBlank: false
        },
        {
            name: "rd",
            xtype: "textfield",
            fieldLabel: "RD",
            allowBlank: false
        },
        {
            name: "afi_ipv4",
            xtype: "checkboxfield",
            boxLabel: "IPv4",
            allowBlank: false
        },
        {
            name: "afi_ipv6",
            xtype: "checkboxfield",
            boxLabel: "IPv6",
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "tt",
            xtype: "textfield",
            regexText: /^\d*$/,
            fieldLabel: "TT",
            allowBlank: true
        },
        {
            name: "tags",
            xtype: "tagsfield",
            fieldLabel: "Tags",
            allowBlank: true
        },
        {
            name: "style",
            xtype: "main.style.LookupField",
            fieldLabel: "Style",
            allowBlank: true
        },
        {
            name: "allocated_till",
            xtype: "datefield",
            fieldLabel: "Allocated till",
            allowBlank: true
        }
    ],
    filters: [
        {
            title: "By VRF Group",
            name: "vrf_group",
            ftype: "lookup",
            lookup: "ip.vrfgroup"
        },
        {
            title: "By IPv4",
            name: "afi_ipv4",
            ftype: "boolean"
        },
        {
            title: "By IPv6",
            name: "afi_ipv6",
            ftype: "boolean"
        }
    ]
});
