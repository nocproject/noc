//---------------------------------------------------------------------
// ip.address application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.address.Application");

Ext.define("NOC.ip.address.Application", {
    extend: "NOC.core.ModelApplication",
    uses: [
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
            text: "Name",
            dataIndex: "name"
        }*/
    ],
    fields: [
        {
            name: "prefix",
            xtype: "ip.prefix.LookupField",
            fieldLabel: "Prefix",
            allowBlank: false
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
            name: "address",
            xtype: "textfield",
            fieldLabel: "Address",
            allowBlank: false
        },
        {
            name: "fqdn",
            xtype: "textfield",
            fieldLabel: "FQDN",
            allowBlank: false
        },
        {
            name: "mac",
            xtype: "textfield",
            fieldLabel: "MAC",
            allowBlank: true
        },
        {
            name: "auto_update_mac",
            xtype: "checkboxfield",
            boxLabel: "Auto Update MAC",
            allowBlank: false
        },
        {
            name: "managed_object",
            xtype: "sa.managedobject.LookupField",
            fieldLabel: "Managed Object",
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
            xtype: "ip.address.LookupField",
            fieldLabel: "ipv6 transition",
            allowBlank: true
        },
        {
            name: "customer",
            xtype: "textfield",
            fieldLabel: "customer",
            allowBlank: true
        }
    ]
});
