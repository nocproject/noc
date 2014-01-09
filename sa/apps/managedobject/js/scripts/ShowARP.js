//---------------------------------------------------------------------
// ShowARP
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.ShowARP");

Ext.define("NOC.sa.managedobject.scripts.ShowARP", {
    extend: "NOC.sa.managedobject.scripts.TablePreview",
    columns: [
        {
            text: "IP",
            dataIndex: "ip",
            width: 100
        },
        {
            text: "MAC",
            dataIndex: "mac",
            width: 120
        },
        {
            text: "Interface",
            dataIndex: "interface",
            flex: 1
        }
    ],
    search: true
});
