//---------------------------------------------------------------------
// peer.as Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.as.Model");

Ext.define("NOC.peer.as.Model", {
    extend: "Ext.data.Model",
    rest_url: "/peer/as/",

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
            name: "organisation",
            type: "string"
        },
        {
            name: "tags",
            type: "auto",
        }
    ]
});
