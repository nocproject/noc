//---------------------------------------------------------------------
// ip.address application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.address.Application");

Ext.define("NOC.ip.address.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.ip.address.Model",
        "NOC.ip.prefix.LookupField",
        "NOC.ip.vrf.LookupField",
        "NOC.sa.managedobject.LookupField",
        "NOC.main.style.LookupField",
        "NOC.main.resourcestate.LookupField",
        "NOC.ip.address.LookupField"
    ],
    model: "NOC.ip.address.Model",
    columns: [
        /*
        {
            text: __("Name"),
            dataIndex: "name"
        }*/
    ],
    fields: [
        {
            name: "prefix",
            xtype: "ip.prefix.LookupField",
            fieldLabel: __("Prefix"),
            allowBlank: false
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
            name: "address",
            xtype: "textfield",
            fieldLabel: __("Address"),
            allowBlank: false
        },
        {
            name: "fqdn",
            xtype: "textfield",
            fieldLabel: __("FQDN"),
            allowBlank: false
        },
        {
            name: "mac",
            xtype: "textfield",
            fieldLabel: __("MAC"),
            allowBlank: true
        },
        {
            name: "auto_update_mac",
            xtype: "checkboxfield",
            boxLabel: __("Auto Update MAC"),
            allowBlank: false
        },
        {
            name: "managed_object",
            xtype: "sa.managedobject.LookupField",
            fieldLabel: __("Managed Object"),
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
            xtype: "ip.address.LookupField",
            fieldLabel: __("ipv6 transition"),
            allowBlank: true
        },
        {
            name: "customer",
            xtype: "textfield",
            fieldLabel: __("customer"),
            allowBlank: true
        }
    ]
});
