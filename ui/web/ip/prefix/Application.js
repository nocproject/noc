//---------------------------------------------------------------------
// ip.prefix application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.prefix.Application");

Ext.define("NOC.ip.prefix.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
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
            text: "Name",
            dataIndex: "name"
        }*/
    ],
    fields: [
        {
            name: "parent",
            xtype: "ip.prefix.LookupField",
            fieldLabel: "Parent",
            allowBlank: true
        },
        {
            name: "vrf",
            xtype: "ip.vrf.LookupField",
            fieldLabel: "VRF",
            allowBlank: false
        },
        {
            name: "afi",
            xtype: "textfield",
            fieldLabel: "Address Family",
            allowBlank: false
        },
        {
            name: "prefix",
            xtype: "textfield",
            fieldLabel: "Prefix",
            allowBlank: false
        },
        {
            name: "asn",
            xtype: "peer.as.LookupField",
            fieldLabel: "AS",
            allowBlank: false
        },
        {
            name: "vc",
            xtype: "vc.vc.LookupField",
            fieldLabel: "VC",
            allowBlank: true
        },
        {
            name: "description",
            xtype: "textarea",
            fieldLabel: "Description",
            allowBlank: true
        },
        {
            name: "tags",
            xtype: "tagsfield",
            fieldLabel: "Tags",
            allowBlank: true
        },
        {
            name: "tt",
            xtype: "numberfield",
            fieldLabel: "TT",
            allowBlank: true
        },
        {
            name: "style",
            xtype: "main.style.LookupField",
            fieldLabel: "Style",
            allowBlank: true
        },
        {
            name: "state",
            xtype: "main.resourcestate.LookupField",
            fieldLabel: "State",
            allowBlank: false
        },
        {
            name: "allocated_till",
            xtype: "datefield",
            fieldLabel: "Allocated till",
            allowBlank: true
        },
        {
            name: "ipv6_transition",
            xtype: "ip.prefix.LookupField",
            fieldLabel: "ipv6 transition",
            allowBlank: true
        },
        {
            name: "service",
            xtype: "textfield",
            fieldLabel: "service",
            allowBlank: true
        },
        {
            name: "site",
            xtype: "textfield",
            fieldLabel: "site",
            allowBlank: true
        },
        {
            name: "is_primary",
            xtype: "checkboxfield",
            boxLabel: "is primary",
            allowBlank: false
        },
        {
            name: "host",
            xtype: "textfield",
            fieldLabel: "host",
            allowBlank: true
        },
        {
            name: "last_changed",
            xtype: "datefield",
            fieldLabel: "last changed",
            allowBlank: true
        },
        {
            name: "last_changed_by",
            xtype: "textfield",
            fieldLabel: "last changed by",
            allowBlank: true
        },
        {
            name: "customer",
            xtype: "textfield",
            fieldLabel: "customer",
            allowBlank: true
        },
        {
            name: "division",
            xtype: "textfield",
            fieldLabel: "division",
            allowBlank: true
        },
        {
            name: "vlan",
            xtype: "numberfield",
            fieldLabel: "vlan",
            allowBlank: true
        },
        {
            name: "origin",
            xtype: "textfield",
            fieldLabel: "origin",
            allowBlank: true
        },
        {
            name: "cluster",
            xtype: "textfield",
            fieldLabel: "cluster",
            allowBlank: true
        },
        {
            name: "project",
            xtype: "textfield",
            fieldLabel: "project",
            allowBlank: true
        }
    ]
});
