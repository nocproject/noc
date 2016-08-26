//---------------------------------------------------------------------
// sa.authprofile SuggestCLIModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.authprofile.SuggestCLIModel");

Ext.define("NOC.sa.authprofile.SuggestCLIModel", {
    extend: "Ext.data.Model",
    rest_url: "/sa/authprofile/{{parent}}/suggest_cli/",
    parentField: "auth_profile_id",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "user",
            type: "string"
        },
        {
            name: "password",
            type: "string"
        },
        {
            name: "super_password",
            type: "string"
        }
    ]
});

