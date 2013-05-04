//---------------------------------------------------------------------
// wf.workflow Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.workflow.Model");

Ext.define("NOC.wf.workflow.Model", {
    extend: "Ext.data.Model",
    rest_url: "/wf/workflow/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "display_name",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean"
        },
        {
            name: "solution",
            type: "string"
        },
        {
            name: "solution__label",
            type: "string",
            persist: false
        },
        {
            name: "start_node",
            type: "string"
        },
        {
            name: "version",
            type: "int"
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
