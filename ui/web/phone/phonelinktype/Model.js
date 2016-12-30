//---------------------------------------------------------------------
// phone.phonelinktype Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.phonelinktype.Model");

Ext.define("NOC.phone.phonelinktype.Model", {
    extend: "Ext.data.Model",
    rest_url: "/phone/phonelinktype/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "code",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean"
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
