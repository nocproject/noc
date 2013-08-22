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
            type: "string"
        },
        {
            name: "name",
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
        }
    ]
});
