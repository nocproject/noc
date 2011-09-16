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
    
    columns: [
        {
            text: "Name",
            dataIndex: "type"
        },
        {
            text: "Active",
            dataIndex: "is_active"
        },
        {
            text: "Validation",
            dataIndex: "validation"
        }
    ],
    
    fields: [
        {
            xtype: "textfield",
            fieldLabel: "Name",
            name: "name",
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
    ]
});
