//---------------------------------------------------------------------
// peer.peer Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.peer.Model");

Ext.define("NOC.peer.peer.Model", {
    extend: "Ext.data.Model",
    rest_url: "/peer/peer/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "peer_group",
            type: "string"
        },
        {
            name: "peer_group__label",
            type: "string",
            persist:false
        },
        {
            name: "peering_point",
            type: "string"
        },
        {
            name: "peering_point__label",
            type: "string",
            persist:false
        },
        {
            name: "project",
            type: "int"
        },
        {
            name: "project__label",
            type: "string",
            persist: false
        },
        {
            name: "local_asn",
            type: "string"
        },
        {
            name: "local_asn__label",
            type: "string",
            persist:false
        },
        {
            name: "local_ip",
            type: "string"
        },
        {
            name: "local_backup_ip",
            type: "string"
        },
        {
            name: "remote_asn", 
            type: "int"
        },
        {
            name: "remote_ip",
            type: "string"
        },
        {
            name: "remote_backup_ip",
            type: "string"
        },
        {
            name: "status",
            type: "string",
            defaultValue: "A"
        },
        {
            name: "import_filter",
            type: "string"
        },
        {
            name: "local_pref",
            type: "int"
        },
        {
            name: "import_med",      
            type: "int"
        },
        {
            name: "export_med",      
            type: "int"
        },
        {
            name: "export_filter",      
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "rpsl_remark",
            type: "string"
        },
        {
            name: "tt",
            type: "int"
        },
        {
            name: "communities",  
            type: "string"
        },
        {
            name: "max_prefixes",  
            type: "int",
            defaultValue: "100"
        },
        {
            name: "import_filter_name",
            type: "string"
        },
        {
            name: "export_filter_name",
            type: "string"
        },
        {
            name: "tags",
            type: "string"
        }
    ]
});
