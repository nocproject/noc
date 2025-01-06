//---------------------------------------------------------------------
// peer.peerprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.peerprofile.Model");

Ext.define("NOC.peer.peerprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/peer/peerprofile/",

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
            name: "workflow",
            type: "string"
        },
        {
            name: "max_prefixes",
            defaultValue: 100,
            type: "int"
        },
        {
            name: "status_discovery",
            type: "string"
        },
        {
            name: "status_change_notification",
            type: "string"
        },
        {
            name: "data",
            type: "auto"
        }
    ]
});
