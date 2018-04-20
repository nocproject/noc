//---------------------------------------------------------------------
// main.notificationgroup Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.notificationgroup.UsersModel");

Ext.define("NOC.main.notificationgroup.UsersModel", {
    extend: "Ext.data.Model",
    rest_url: "/main/notificationgroup/{{parent}}/users/",
    parentField: "notification_group_id",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "time_pattern",
            type: "int"
        },
        {
            name: "time_pattern__label",
            type: "string",
            persist: false
        },
        {
            name: "user",
            type: "int"
        },
        {
            name: "user__label",
            type: "string",
            persist: false
        }
    ]
});
