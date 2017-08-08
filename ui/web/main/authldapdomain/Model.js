//---------------------------------------------------------------------
// main.authldapdomain Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.authldapdomain.Model");

Ext.define("NOC.main.authldapdomain.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/authldapdomain/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "deny_group",
            type: "string"
        },
        {
            name: "bind_user",
            type: "string"
        },
        {
            name: "groups",
            type: "auto"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "root",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean"
        },
        {
            name: "is_default",
            type: "boolean"
        },
        {
            name: "group_search_filter",
            type: "string"
        },
        {
            name: "servers",
            type: "auto"
        },
        {
            name: "require_group",
            type: "string"
        },
        {
            name: "bind_password",
            type: "string"
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "user_search_filter",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "require_any_group",
            type: "boolean"
        },
        {
            name: "convert_username",
            type: "string"
        },
        {
            name: "sync_name",
            type: "boolean"
        },
        {
            name: "sync_mail",
            type: "boolean"
        }
    ]
});
