//---------------------------------------------------------------------
// peer.asprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.asprofile.Model");

Ext.define("NOC.peer.asprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/peer/asprofile/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "enable_discovery_prefix_whois_route",
            type: "boolean"
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
            name: "prefix_profile_whois_route",
            type: "string"
        },
        {
            name: "prefix_profile_whois_route__label",
            type: "string",
            persist: false
        }
    ]
});
