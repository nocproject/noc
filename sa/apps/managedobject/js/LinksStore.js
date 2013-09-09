//---------------------------------------------------------------------
// sa.managedobject L2 Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.LinksStore");

Ext.define("NOC.sa.managedobject.LinksStore", {
    extend: "Ext.data.Store",
    model: null,
    fields: [
        {
            name: "local_interface",
            type: "string"
        },
        {
            name: "local_interface__label",
            type: "string"
        },
        {
            name: "remote_object",
            type: "string"
        },
        {
            name: "remote_object__label",
            type: "string"
        },
        {
            name: "remote_interface",
            type: "string"
        },
        {
            name: "remote_interface__label",
            type: "string"
        },
        {
            name: "discovery_method",
            type: "string"
        }
    ],
    data: []
});
