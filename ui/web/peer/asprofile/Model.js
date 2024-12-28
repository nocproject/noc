//---------------------------------------------------------------------
// peer.asprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
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
            type: "boolean",
            defaultValue: false
        },
        {
            name: "enable_discovery_peer",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "gen_rpsl",
            type: "boolean",
            defaultValue: false
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
            name: "style",
            type: "string"
        },
        {
            name: "style__label",
            type: "string",
            persist: false
        },
        {
            name: "prefix_profile_whois_route",
            type: "string"
        },
        {
            name: "prefix_profile_whois_route__label",
            type: "string",
            persist: false
        },
        {
            name: "validation_policy",
            type: "string",
            defaultValue: "O"
        },
        {
            name: "dynamic_classification_policy",
            type: "string",
            defaultValue: "R"
        },
        {
            name: "match_rules",
            type: "auto"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
