//---------------------------------------------------------------------
// crm.subscriberprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.subscriberprofile.Model");

Ext.define("NOC.crm.subscriberprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/crm/subscriberprofile/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "style",
            type: "int"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "tags",
            type: "auto"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
