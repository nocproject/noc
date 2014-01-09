//---------------------------------------------------------------------
// ShowMAC
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.ShowMAC");

Ext.define("NOC.sa.managedobject.scripts.ShowMAC", {
    extend: "NOC.sa.managedobject.scripts.TablePreview",
    columns: [
        {
            text: "MAC",
            dataIndex: "mac",
            width: 120
        },
        {
            text: "Type",
            dataIndex: "type",
            width: 70,
            renderer: NOC.render.Choices({
                D: "DYNAMIC",
                S: "STATIC"
            })
        },
        {
            text: "VLAN",
            dataIndex: "vlan_id",
            width: 50
        },
        {
            text: "Interface",
            dataIndex: "interfaces",
            flex: 1,
            renderer: NOC.render.Join(", ")
        }
    ],
    search: true
});
