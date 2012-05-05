//---------------------------------------------------------------------
// sa.monitor PoolsStore
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.monitor.PoolsStore");

Ext.define("NOC.sa.monitor.PoolsStore", {
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
            name: "state",
            type: "string"
        },
        {
            name: "current_scripts",
            type: "int"
        },
        {
            name: "max_scripts",
            type: "int"
        }
    ],
    data: []
});
