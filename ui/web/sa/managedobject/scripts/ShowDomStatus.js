//---------------------------------------------------------------------
// ShowDomStatus
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.ShowDomStatus");

Ext.define("NOC.sa.managedobject.scripts.ShowDomStatus", {
    extend: "NOC.sa.managedobject.scripts.TablePreview",
    columns: [
        {
            text: __("Interface"),
            dataIndex: "interface",
            width: 120,
        },
        {
            text: __("Temp, C"),
            dataIndex: "temp_c",
            width: 70,
        },
        {
            text: __("Voltage, V"),
            dataIndex: "voltage_v",
            width: 70,
        },
        {
            text: __("Current, mA"),
            dataIndex: "current_ma",
            width: 70,
        },
        {
            text: __("Optical Tx, bBm"),
            dataIndex: "optical_tx_dbm",
            width: 90,
        },
        {
            text: __("Optical Rx, bBm"),
            dataIndex: "optical_rx_dbm",
            width: 90,
            flex: 1
        }
    ],
    search: true
});
