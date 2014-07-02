//---------------------------------------------------------------------
// ip.addressrange application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.addressrange.Application");

Ext.define("NOC.ip.addressrange.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.ip.addressrange.Model",
        "NOC.ip.vrf.LookupField"
    ],
    model: "NOC.ip.addressrange.Model",
    search: true,
    rowClassField: "row_class",
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            flex: 1
        },
        {
            dataIndex: "is_active",
            text: "Active?",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "VRF",
            dataIndex: "vrf",
            renderer: NOC.render.Lookup("vrf")
        },
        {
            text: "AFI",
            dataIndex: "afi",
            width: 40,
            renderer: function(v) {
                return "IPv" + v;
            }
        },
        {
            text: "From Address",
            dataIndex: "from_address",
            width: 80
        },
        {
            text: "To Address", 
            dataIndex: "to_address",
            width: 80
        },
        {
            dataIndex: "is_locked",
            text: "Locked?",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "Action",
            dataIndex: "action",
            renderer: function(a) {
                return {N: "Do nothing", G: "Generate FQDNs", D: "Partial reverse zone delegation"}[a];
            }
        },
        {
            text: "Description",
            dataIndex: "description"
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
            fieldLabel: "Name",
            allowBlank: false
        },
        {
            name: "is_active",
            xtype: "checkboxfield",
            boxLabel: "Is Active"
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
            store: [["4", "IPv4"], ["6", "IPv6"]]
        },
        {
            name: "from_address",
            xtype: "textfield",
            fieldLabel: "From Address",
            allowBlank: false
        },
        {
            name: "to_address",
            xtype: "textfield",
            fieldLabel: "To Address",
            allowBlank: false
        },
        {
            name: "description",
            xtype: "textareafield",
            fieldLabel: "Description",
            allowBlank: false,
            anchor: "70%"
        },
        {
            name: "is_locked",
            xtype: "checkboxfield",
            boxLabel: "Is Locked"
        },
        {
            name: "action",
            xtype: "combobox",
            fieldLabel: "Action",
            allowBlank: false,
            store: [
                ["N", "Do nothing"],
                ["G", "Generate FQDNs"],
                ["D", "Partial reverse zone delegation"]
            ]
        },
        {
            name: "fqdn_template",
            xtype: "textfield",
            allowBlank: true,
            fieldLabel: "FQDN Template"
        },
        {
            name: "reverse_nses",
            xtype: "textfield",
            allowBlank: true,
            fieldLabel: "Reverse NSes"
        },
        {
            name: "tags",
            xtype: "tagsfield",
            fieldLabel: "Tags",
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
            name: "allocated_till",
            xtype: "datefield",
            fieldLabel: "Allocated till",
            allowBlank: true
        }
    ],
    filters: [
        {
            title: "By Is Active",
            name: "is_active",
            ftype: "boolean"
        },
        {  
            title: "By VRF",   
            name: "vrf",   
            ftype: "lookup",
            lookup: "ip.vrf"
        },
        {  
            title: "By Is Locked",   
            name: "is_locked",   
            ftype: "boolean"
        }
    ],
    showOpError: function(action, op, status) {
        var me = this;
        // Detect Syntax Errors
        if(status.traceback) {
            NOC.error(status.traceback);
            return;
        }
        me.callParent([action, op, status]);
    }
});
