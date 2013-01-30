//---------------------------------------------------------------------
// sa.monitor ScriptsStore
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.monitor.ScriptsStore");

Ext.define("NOC.sa.monitor.ScriptsStore", {
    extend: "Ext.data.Store",
    model: null,
    groupField: "pool",
    fields: [
        {
            name: "pool",
            type: "string"
        },
        {
            name: "instance",
            type: "string"
        },
        {
            name: "script",
            type: "string"
        },
        {
            name: "object_name",
            type: "string"
        },
        {
            name: "address",
            type: "string"
        },
        {
            name: "start_time",
            type: "date"
        },
        {
            name: "timeout",
            type: "int"
        },
        {
            name: "duration",
            type: "int"
        }
    ],
    data: []
});
