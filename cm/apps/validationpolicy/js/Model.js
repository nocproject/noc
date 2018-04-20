//---------------------------------------------------------------------
// cm.validationpolicy Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.validationpolicy.Model");

Ext.define("NOC.cm.validationpolicy.Model", {
    extend: "Ext.data.Model",
    rest_url: "/cm/validationpolicy/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "rules",
            type: "auto"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
