//---------------------------------------------------------------------
// ip.prefixaccess application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.prefixaccess.Application");

Ext.define("NOC.ip.prefixaccess.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.ip.prefixaccess.Model",
        "NOC.main.user.LookupField",
        "NOC.ip.vrf.LookupField"
    ],
    model: "NOC.ip.prefixaccess.Model",
    search: true,
    columns: [
        {
            text: "User",
            dataIndex: "user",
            renderer: NOC.render.Lookup("user")
        },
        {
            text: "VRF",
            dataIndex: "vrf",
            renderer: NOC.render.Lookup("vrf")
        },
        {
            text: "AFI",
            dataIndex: "afi",
            renderer: function(v) { return "IPv" + v; }
        },
        {
            text: "Prefix",
            dataIndex: "prefix"
        },
        {
            text: "View",
            dataIndex: "can_view",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "Change",
            dataIndex: "can_change",
            renderer: NOC.render.Bool,
            width: 50
        }
    ],
    fields: [
        {
            name: "user",
            xtype: "main.user.LookupField",
            fieldLabel: "User",
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
            xtype: "combobox",
            fieldLabel: "Address Family",
            allowBlank: false,
            queryMode: "local",
            displayField: "label",
            valueField: "id",
            store: {
                fields: ["id", "label"],
                data: [
                    {id: "4", label: "IPv4"},
                    {id: "6", label: "IPv6"}
                ]
            }
        },
        {
            name: "prefix",
            xtype: "textfield",
            fieldLabel: "Prefix",
            allowBlank: false
        },
        {
            name: "can_view",
            xtype: "checkboxfield",
            boxLabel: "Can View",
            allowBlank: false
        },
        {
            name: "can_change",
            xtype: "checkboxfield",
            boxLabel: "Can Change",
            allowBlank: false
        }
    ],
    filters: [
        {
            title: "By User",
            name: "user",
            ftype: "lookup",
            lookup: "main.user"
        },
        {
            title: "By VRF",
            name: "vrf",
            ftype: "lookup",
            lookup: "ip.vrf"
        },
        {
            title: "By AFI",
            name: "afi",
            ftype: "afi"
        },
        {
            title: "By Can View",
            name: "can_view",
            ftype: "boolean"
        },
        {
            title: "By Can Change",
            name: "can_change",
            ftype: "boolean"
        }
    ]
});
