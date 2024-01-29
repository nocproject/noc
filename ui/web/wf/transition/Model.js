//---------------------------------------------------------------------
// wf.transition Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.transition.Model");

Ext.define("NOC.wf.transition.Model", {
    extend: "Ext.data.Model",
    rest_url: "/wf/transition/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "workflow",
            type: "string"
        },
        {
            name: "workflow__label",
            type: "string",
            persist: false
        },
        {
            name: "from_state",
            type: "string"
        },
        {
            name: "from_state__label",
            type: "string",
            persist: false
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "to_state",
            type: "string"
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
            name: "label",
            type: "string"
        },
        {
            name: "event",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "enable_manual",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "bi_id",
            type: "int",
            persist: false
        },
        {
            name: "event",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "required_rules",
            type: "auto",
        },
        {
            name: "handlers",
            type: "auto"
        }
    ]
});
