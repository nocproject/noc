//---------------------------------------------------------------------
// phone.phonerangeprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.phonerangeprofile.Model");

Ext.define("NOC.phone.phonerangeprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/phone/phonerangeprofile/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "cooldown",
            type: "int",
            defaultValue: 30
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
