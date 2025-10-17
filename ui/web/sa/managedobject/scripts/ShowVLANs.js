//---------------------------------------------------------------------
// ShowVLANs
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.ShowVLANs");

Ext.define("NOC.sa.managedobject.scripts.ShowVLANs", {
  extend: "NOC.sa.managedobject.scripts.TablePreview",
  columns: [
    {
      text: __("VLAN"),
      dataIndex: "vlan_id",
      width: 50,
    },
    {
      text: __("Name"),
      dataIndex: "name",
      flex: 1,
    },
  ],
  search: true,
});
