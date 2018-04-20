//---------------------------------------------------------------------
// wf.solution Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.solution.Model");

Ext.define("NOC.wf.solution.Model", {
    extend: "Ext.data.Model",
    rest_url: "/wf/solution/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "version",
            type: "int"
        },
        {
            name: "is_active",
            type: "boolean"
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
            name: "wf_count",
            type: "int",
            persist: false
        }
    ]
});
