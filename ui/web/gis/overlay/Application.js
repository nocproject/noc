//---------------------------------------------------------------------
// gis.overlay application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.gis.overlay.Application");

Ext.define("NOC.gis.overlay.Application", {
  extend: "NOC.core.ModelApplication",
  requires: ["NOC.gis.overlay.Model"],
  model: "NOC.gis.overlay.Model",
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
    },
    {
      text: __("Gate Id"),
      dataIndex: "gate_id",
    },
    {
      text: __("Active"),
      dataIndex: "is_active",
    },
    {
      text: __("Plugin"),
      dataIndex: "plugin",
    },
    {
      text: __("Permission"),
      dataIndex: "permission_name",
    },
  ],
  fields: [
    {
      name: "name",
      xtype: "textfield",
      fieldLabel: __("Name"),
      allowBlank: false,
    },
    {
      name: "gate_id",
      xtype: "textfield",
      fieldLabel: __("Gate Id"),
      allowBlank: false,
      regex: /^[a-zA-Z0-9_-]+$/,
    },
    {
      name: "Active",
      xtype: "checkboxfield",
      boxLabel: __("is_active"),
    },
    {
      name: "Plugin",
      xtype: "textfield",
      fieldLabel: __("plugin"),
      allowBlank: false,
    },
    {
      name: "Permission",
      xtype: "textfield",
      fieldLabel: __("permission_name"),
      allowBlank: false,
    },
  ],
});
