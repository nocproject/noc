//---------------------------------------------------------------------
// ShowChassisID
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.ShowChassisID");

Ext.define("NOC.sa.managedobject.scripts.ShowChassisID", {
  extend: "NOC.sa.managedobject.scripts.TablePreview",
  columns: [
    {
      text: __("First MAC"),
      dataIndex: "first_chassis_mac",
      width: 120,
    },
    {
      text: __("Last MAC"),
      dataIndex: "last_chassis_mac",
      width: 120,
      flex: 1,
    },
  ],
  search: true,
});
