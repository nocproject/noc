//---------------------------------------------------------------------
// dns.rrtype Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.rrtype.Model");

Ext.define("NOC.dns.rrtype.Model", {
    extend: "Ext.data.Model",
    rest_url: "/dns/rrtype/",

    fields: [
        {
            name: "id",
            type: "int"
        },

        {
            name: "type",
            type: "string"
        },
        
        {
            name: "is_active",
            type: "boolean",
            defaultValue: false
        },
        
        {
            name: "validation",
            type: "string"  // @todo: NULL
        }
    ]
});
