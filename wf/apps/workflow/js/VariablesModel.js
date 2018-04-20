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
            name: "type",
            type: "string"
        },
        {
            name: "default",
            type: "string"
        },
        {
            name: "required",
            type: "boolean"
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
