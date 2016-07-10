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
            name: "description",
            type: "string"
        }
    ]
});
