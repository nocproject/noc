//---------------------------------------------------------------------
// sa.serviceprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.serviceprofile.Model");

Ext.define("NOC.sa.serviceprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/serviceprofile/",

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
            name: "card_title_template",
            type: "string"
        },
        {
            name: "glyph",
            type: "string"
        }
    ]
});
