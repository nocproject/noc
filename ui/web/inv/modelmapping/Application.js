//---------------------------------------------------------------------
// inv.modelmapping application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.modelmapping.Application");

Ext.define("NOC.inv.modelmapping.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.inv.modelmapping.Model",
    "NOC.inv.objectmodel.LookupField",
  ],
  model: "NOC.inv.modelmapping.Model",
  columns: [
    {
      text: __("Vendor"),
      dataIndex: "vendor",
      width: 100,
    },
    {
      text: __("Part No"),
      dataIndex: "part_no",
      width: 75,
    },
    {
      text: __("From serial"),
      dataIndex: "from_serial",
      width: 75,
    },
    {
      text: __("To serial"),
      dataIndex: "to_serial",
      width: 75,
    },
    {
      text: __("Model"),
      dataIndex: "model",
      renderer: NOC.render.Lookup("model"),
      width: 200,
    },
    {
      text: __("Active"),
      dataIndex: "is_active",
      renderer: NOC.render.Bool,
      width: 50,
    },
    {
      text: __("Description"),
      dataIndex: "description",
      flex: 1,
    },
  ],
  fields: [
    {
      name: "vendor",
      xtype: "textfield",
      fieldLabel: __("Vendor"),
      allowBlank: false,
    },
    {
      name: "part_no",
      xtype: "textfield",
      fieldLabel: __("Part No"),
      allowBlank: true,
    },
    {
      name: "from_serial",
      xtype: "textfield",
      fieldLabel: __("From Serial"),
      allowBlank: true,
    },
    {
      name: "to_serial",
      xtype: "textfield",
      fieldLabel: __("To Serial"),
      allowBlank: true,
    },
    {
      name: "model",
      xtype: "inv.objectmodel.LookupField",
      fieldLabel: __("Model"),
      uiStyle: "large",
      allowBlank: false,
    },
    {
      name: "is_active",
      xtype: "checkboxfield",
      boxLabel: __("Active"),
    },
    {
      name: "description",
      xtype: "textarea",
      fieldLabel: __("Description"),
      allowBlank: true,
    },
  ],
});
