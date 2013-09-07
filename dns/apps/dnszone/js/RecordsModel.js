//---------------------------------------------------------------------
// dns.dnszone Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnszone.RecordsModel");

Ext.define("NOC.dns.dnszone.RecordsModel", {
    extend: "Ext.data.Model",
    rest_url: "/dns/dnszone/{{parent}}/records/",
    parentField: "zone_id",

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
            name: "ttl",
            type: "integer",
            useNull: true
        },
        {
            name: "priority",
            type: "integer",
            useNull: true
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "content",
            type: "string"
        },
        {
            name: "tags",
            type: "auto"
        }
    ]
});
