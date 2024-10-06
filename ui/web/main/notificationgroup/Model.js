//---------------------------------------------------------------------
// main.notificationgroup Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.notificationgroup.Model");

Ext.define("NOC.main.notificationgroup.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/notificationgroup/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
          name: "uuid",
          type: "string",
          persist: false,
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "message_register_policy",
            type: "string",
            defaultValue: "d"
        },
        {
            name: "message_types",
            type: "auto"
        },
        {
            name: "subscription_settings",
            type: "auto"
        },
        {
            name: "static_members",
            type: "auto"
        },
        {
            name: "conditions",
            type: "auto"
        }
    ]
});
