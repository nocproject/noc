//---------------------------------------------------------------------
// sa.managedobject Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug("Defining NOC.sa.managedobject.ApplicationModel");
Ext.define("NOC.sa.managedobject.ApplicationModel", {
    extend: "Ext.data.Model",
    rest_url: "/sa/objectlist/",
    actionMethods: {
        read: 'POST'
    },

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
            name: "address",
            type: "string"
        },
        {
            name: "profile",
            type: "string"
        },
        {
            name: "platform",
            type: "string"
        },
        {
            name: "version",
            type: "string"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        },
        {
            name: 'status',
            defaultValue: 'w',
            persist: false
        },
        {
            name: 'result',
            persist: false
        }
    ]
});
