//---------------------------------------------------------------------
// wf.workflow Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
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
            name: "remote_id",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "allowed_models",
            type: "auto"
        },
        {
            name: "remote_system",
            type: "string"
        },
        {
            name: "remote_system__label",
            type: "string",
            persist: false
        },
        {
            name: "is_active",
            type: "boolean"
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
