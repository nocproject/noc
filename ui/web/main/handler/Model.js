//---------------------------------------------------------------------
// main.handler Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.handler.Model");

Ext.define("NOC.main.handler.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/handler/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "handler",
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
            name: "is_builtin",
            type: "boolean",
            persist: false
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "allow_config_filter",
            type: "boolean"
        },
        {
            name: "allow_config_validation",
            type: "boolean"
        },
        {
            name: "allow_config_diff",
            type: "boolean"
        },
        {
            name: "allow_config_diff_filter",
            type: "boolean"
        },
        {
            name: "allow_housekeeping",
            type: "boolean"
        },
        {
            name: "allow_resolver",
            type: "boolean"
        },
        {
            name: "allow_threshold",
            type: "boolean"
        },
        {
            name: "allow_threshold_handler",
            type: "boolean"
        },
        {
            name: "allow_threshold_value_handler",
            type: "boolean"
        },
        {
            name: "allow_ds_filter",
            type: "boolean"
        },
        {
            name: "allow_ifdesc",
            type: "boolean"
        },
        {
            name: "allow_mx_transmutation",
            type: "boolean"
        },
        {
            name: "allow_match_rule",
            type: "boolean"
        }
    ]
});
