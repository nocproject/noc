//---------------------------------------------------------------------
// Lanes model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.workflow.LanesModel");

Ext.define("NOC.wf.workflow.LanesModel", {
    extend: "Ext.data.Model",
    rest_url: "/wf/workflow/{{parent}}/lanes/",
    parentField: "workflow",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "workflow",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean"
        }
    ]
});
