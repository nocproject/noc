//---------------------------------------------------------------------
// ShowInterfaceStatus
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.ShowInterfaceStatus");

Ext.define("NOC.sa.managedobject.scripts.ShowInterfaceStatus", {
    extend: "NOC.sa.managedobject.scripts.TablePreview",
    columns: [
        {
            text: "Interface",
            dataIndex: "interface",
            width: 120,
        },
        {
            text: "Status",
            dataIndex: "status",
            renderer: NOC.render.Bool,
            flex: 1
        }
    ],
    search: true
});
