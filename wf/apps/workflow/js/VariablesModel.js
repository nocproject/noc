//---------------------------------------------------------------------
// Variables model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.workflow.VariablesModel");

Ext.define("NOC.wf.workflow.VariablesModel", {
    extend: "Ext.data.Model",
    rest_url: "/wf/workflow/{{parent}}/variables/",
    parentField: "workflow",

    fields: [
        {
            name: "id",
            type: "str"
        },
        {
            name: "workflow",
            type: "str"
        },
        {
            name: "name",
            type: "str"
        },
        {
            name: "type",
            type: "str"
        },
        {
            name: "default",
            type: "str"
        },
        {
            name: "required",
            type: "boolean"
        },
        {
            name: "description",
            type: "str"
        }
    ]
});
