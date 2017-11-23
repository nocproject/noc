//---------------------------------------------------------------------
// wf.state Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.state.Model");

Ext.define("NOC.wf.state.Model", {
    extend: "Ext.data.Model",
    rest_url: "/wf/state/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "update_expired",
            type: "boolean"
        },
        {
            name: "is_productive",
            type: "boolean"
        },
        {
            name: "on_enter_handlers",
            type: "auto"
        },
        {
            name: "workflow",
            type: "string"
        },
        {
            name: "job_handler",
            type: "string"
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "update_ttl",
            type: "boolean"
        },
        {
            name: "is_default",
            type: "boolean"
        },
        {
            name: "remote_system",
            type: "string"
        },
        {
            name: "ttl",
            type: "int"
        },
        {
            name: "on_leave_handlers",
            type: "auto"
        },
        {
            name: "bi_id",
            type: "int"
        },
        {
            name: "name",
            type: "string"
        }
    ]
});
