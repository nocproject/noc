//---------------------------------------------------------------------
// ip.prefix application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.prefix.Application");

Ext.define("NOC.ip.prefix.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.ip.prefix.Model",
        "NOC.ip.prefix.LookupField",
        "NOC.ip.vrf.LookupField",
        "NOC.peer.as.LookupField",
        "NOC.vc.vc.LookupField",
        "NOC.main.style.LookupField",
        "NOC.main.resourcestate.LookupField",
        "NOC.ip.prefix.LookupField"
    ],
    model: "NOC.ip.prefix.Model",
    columns: [
        /*
        {
            text: __("Name"),
            dataIndex: "name"
        }*/
    ],
    fields: [
        {
            name: "parent",
            xtype: "ip.prefix.LookupField",
            fieldLabel: __("Parent"),
            allowBlank: true
        },
        {
            name: "vrf",
            xtype: "ip.vrf.LookupField",
            fieldLabel: __("VRF"),
            allowBlank: false
        },
        {
            name: "afi",
            xtype: "textfield",
            fieldLabel: __("Address Family"),
            allowBlank: false
        },
        {
            name: "prefix",
            xtype: "textfield",
            fieldLabel: __("Prefix"),
            allowBlank: false
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
            name: "description",
            xtype: "textarea",
            fieldLabel: __("Description"),
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
            name: "style",
            xtype: "main.style.LookupField",
            fieldLabel: __("Style"),
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
            name: "service",
            xtype: "textfield",
            fieldLabel: __("service"),
            allowBlank: true
        },
        {
            name: "site",
            xtype: "textfield",
            fieldLabel: __("site"),
            allowBlank: true
        },
        {
            name: "is_primary",
            xtype: "checkboxfield",
            boxLabel: __("is primary"),
            allowBlank: false
        },
        {
            name: "host",
            xtype: "textfield",
            fieldLabel: __("host"),
            allowBlank: true
        },
        {
            name: "last_changed",
            xtype: "datefield",
            startDay: 1,
            fieldLabel: __("last changed"),
            allowBlank: true
        },
        {
            name: "last_changed_by",
            xtype: "textfield",
            fieldLabel: __("last changed by"),
            allowBlank: true
        },
        {
            name: "customer",
            xtype: "textfield",
            fieldLabel: __("customer"),
            allowBlank: true
        },
        {
            name: "division",
            xtype: "textfield",
            fieldLabel: __("division"),
            allowBlank: true
        },
        {
            name: "vlan",
            xtype: "numberfield",
            fieldLabel: __("vlan"),
            allowBlank: true
        },
        {
            name: "origin",
            xtype: "textfield",
            fieldLabel: __("origin"),
            allowBlank: true
        },
        {
            name: "cluster",
            xtype: "textfield",
            fieldLabel: __("cluster"),
            allowBlank: true
        },
        {
            name: "project",
            xtype: "textfield",
            fieldLabel: __("project"),
            allowBlank: true
        }
    ]
});
