//---------------------------------------------------------------------
// peer.maintainer Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.maintainer.Model");

Ext.define("NOC.peer.maintainer.Model", {
    extend: "Ext.data.Model",
    rest_url: "/peer/maintainer/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "maintainer",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "password",
            type: "string"
        },
        {
            name: "rir",
            type: "int"
        },
        {
            name: "rir__label",
            type: "string",
            persist: false
        },
        {
            name: "admins",
            type: "auto"
        },
        {
            name: "extra",
            type: "string"
        }
    ]
});
