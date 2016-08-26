//---------------------------------------------------------------------
// sa.authprofile SuggestSNMPModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.authprofile.SuggestSNMPModel");

Ext.define("NOC.sa.authprofile.SuggestSNMPModel", {
    extend: "Ext.data.Model",
    rest_url: "/sa/authprofile/{{parent}}/suggest_snmp/",
    parentField: "auth_profile_id",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "snmp_ro",
            type: "string"
        },
        {
            name: "snmp_rw",
            type: "string"
        }
    ]
});

