//---------------------------------------------------------------------
// cm.validationrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.cm.validationrule.Model");

Ext.define("NOC.cm.validationrule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/cm/validationrule/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "selectors_list",
            type: "auto"
        },
        {
            name: "objects_list",
            type: "auto"
        },
        {
            name: "config",
            type: "auto"
        },
        {
            name: "handler",
            type: "string"
        }
    ]
});
