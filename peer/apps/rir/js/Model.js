//---------------------------------------------------------------------
// peer.rir Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.rir.Model");

Ext.define("NOC.peer.rir.Model", {
    extend: "Ext.data.Model",
    rest_url: "/peer/rir/",

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
            name: "whois",
            type: "string"
        }
    ]
});
