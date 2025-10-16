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
      xtype: "numbercolumn",
      format: "0.0000",
      width: 100,
      align: "right",
    },
    {
      text: __("Voltage, V"),
      dataIndex: "voltage_v",
      xtype: "numbercolumn",
      format: "0.0000",
      width: 100,
      align: "right",
    },
    {
      text: __("Current, mA"),
      dataIndex: "current_ma",
      xtype: "numbercolumn",
      format: "0.0000",
      width: 100,
      align: "right",
    },
    {
      text: __("Optical Tx, dBm"),
      dataIndex: "optical_tx_dbm",
      xtype: "numbercolumn",
      format: "0.0000",
      width: 110,
      align: "right",
    },
    {
      text: __("Optical Rx, dBm"),
      dataIndex: "optical_rx_dbm",
      xtype: "numbercolumn",
      format: "0.0000",
      width: 110,
      align: "right",
    },
    {
      text: "",
      flex: 1,
    },
  ],
  search: true,
});
