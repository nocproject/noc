//---------------------------------------------------------------------
// pm.metrictype Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metrictype.Model");

Ext.define("NOC.pm.metrictype.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/metrictype/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "uuid",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "scope",
            type: "string"
        },
        {
            name: "measure",
            type: "string"
        },
        {
            name: "vector_tag",
            type: "string"
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        }
    ]
});
