//---------------------------------------------------------------------
// dns.rrtype application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.rrtype.Application");

Ext.define("NOC.dns.rrtype.Application", {
    extend: "NOC.core.ModelApplication",
    uses: ["NOC.dns.rrtype.Model"],
    
    model: "NOC.dns.rrtype.Model",
    search: true,
    
    columns: [
        {
            text: "Type",
            dataIndex: "type"
        },
        {
            text: "Active",
            dataIndex: "is_active",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "Validation",
            dataIndex: "validation",
            flex: 1
        }
    ],
    
    fields: [
        {
            xtype: "textfield",
            fieldLabel: "Type",
            name: "type",
            allowBlank: false
        },
        
        {
            xtype: "checkboxfield",
            boxLabel: "Is Active",
            name: "is_active"
        },
        
        {
            xtype: "textfield",
            fieldLabel: "Validation",
            name: "validation",
            allowBlank: true
        }
    ],
    filters: [
        {
            title: "By Active",
            name: "is_active",
            ftype: "boolean"
        }
    ]
});
