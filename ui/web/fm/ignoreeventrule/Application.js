//---------------------------------------------------------------------
// fm.ignoreeventrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.ignoreeventrule.Application");

Ext.define("NOC.fm.ignoreeventrule.Application", {
  extend: "NOC.core.ModelApplication",
  requires: ["NOC.fm.ignoreeventrule.Model"],
  model: "NOC.fm.ignoreeventrule.Model",
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
    },
    {
      text: __("Active"),
      dataIndex: "is_active",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("Left RE"),
      dataIndex: "left_re",
      flex: 1,
    },
    {
      text: __("Right RE"),
      dataIndex: "right_re",
      flex: 1,
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
      name: "is_active",
      xtype: "checkboxfield",
      boxLabel: __("Is Active"),
      allowBlank: false,
    },
    {
      name: "left_re",
      xtype: "textfield",
      fieldLabel: __("Left RE"),
      allowBlank: false,
    },
    {
      name: "right_re",
      xtype: "textfield",
      fieldLabel: __("Right Re"),
      allowBlank: false,
    },
    {
      name: "description",
      xtype: "textarea",
      fieldLabel: __("Description"),
      allowBlank: true,
    },
  ],
  filters: [
    {
      title: __("By Is Active"),
      name: "is_active",
      ftype: "boolean",
    },
  ],
});
