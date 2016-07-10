//---------------------------------------------------------------------
// main.mimetype Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.mimetype.Model");

Ext.define("NOC.main.mimetype.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/mimetype/",

    fields: [
        {
            name: "id",
            type: "string"
        },

        {
            name: "extension",
            type: "string"
        },

        {
            name: "mime_type",
            type: "string"
        }
    ],
    
    validations: [
        {
            field: "extension",
            type: "format",
            matcher: /^\.[a-zA-Z0-9\-]+$/
        },

        {
            field: "mime_type",
            type: "format",
            matcher: /^[a-zA-Z0-9\-]+\/[a-zA-Z0-9\-]+$/
        }
    ]
});
