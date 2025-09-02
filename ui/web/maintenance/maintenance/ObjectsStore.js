//---------------------------------------------------------------------
// sa.managedobjectselector bufferedStore for ObjectsPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintenance.maintenance.ObjectsStore");

Ext.define("NOC.maintenance.maintenance.ObjectsStore", {
    extend: "Ext.data.BufferedStore",
    alias: "store.maintenance.objects",

    // model: "NOC.maintenance.maintenance.ObjectsModel",
    autoLoad: false,
    pageSize: 70,
    leadingBufferZone: 70,
    numFromEdge: Math.ceil(70 / 2),
    trailingBufferZone: 70,
    purgePageCount: 10,
    remoteSort: true,
    sorters: [
        {
            property: 'address',
            direction: 'DESC'
        }
    ],
    proxy: {
        type: "rest",
        url: "none",
        pageParam: "__page",
        startParam: "__start",
        limitParam: "__limit",
        sortParam: "__sort",
        extraParams: {
            "__format": "ext"
        },
        reader: {
            type: "json",
            rootProperty: "data",
            totalProperty: "total",
            successProperty: "success"
        },
        writer: {
            type: "json"
        }
    }
});
