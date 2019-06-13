//---------------------------------------------------------------------
// main.user Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.user.Model");

Ext.define("NOC.main.user.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/user/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "username",
            type: "string"
        },
        {
            name: "first_name",
            type: "string"
        },
        {
            name: "last_name",
            type: "string"
        },
        {
            name: "email",
            type: "string"
        },
        {
            name: "password",
            type: "string"
        },
        {
            name: "last_login",
            type: "date"
        },
        {
            name: "date_joined",
            type: "date"
        },
        {
            name: "is_superuser",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "is_staff",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "groups",
            type: "auto"
        },
        {
            name: "user_permissions",
            type: "auto"
        }
    ]
});
