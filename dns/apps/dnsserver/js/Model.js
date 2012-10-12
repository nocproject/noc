//---------------------------------------------------------------------
// dns.dnsserver Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnsserver.Model");

Ext.define("NOC.dns.dnsserver.Model", {
    extend: "Ext.data.Model",
    rest_url: "/dns/dnsserver/",

    fields: [
        {
            name: "id",
            type: "int"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "generator_name",
            type: "string"
        },
        {
            name: "ip",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "sync_channel",
            type: "string"
        },
        {
            name: "location",
            type: "string"
        },
        {
            name: "provisioning",
            type: "string"
        },
        {
            name: "autozones_path",
            type: "string",
            defaultValue: "autozones"
        }
    ]
});
