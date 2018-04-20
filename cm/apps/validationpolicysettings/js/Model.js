//---------------------------------------------------------------------
// cm.validationpolicysettings Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.validationpolicysettings.Model");

Ext.define("NOC.cm.validationpolicysettings.Model", {
    extend: "Ext.data.Model",
    rest_url: "/cm/validationpolicysettings/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "model_id",
            type: "string"
        },
        {
            name: "policies",
            type: "auto"
        },
        {
            name: "object_id",
            type: "string"
        }
    ]
});
