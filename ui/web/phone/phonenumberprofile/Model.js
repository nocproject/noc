//---------------------------------------------------------------------
// phone.phonenumberprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.phone.phonenumberprofile.Model");

Ext.define("NOC.phone.phonenumberprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/phone/phonenumberprofile/",

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
        },
        {
            name: "style",
            type: "string"
        },
        {
            name: "style__label",
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
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
