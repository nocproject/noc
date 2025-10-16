//---------------------------------------------------------------------
// main.resourcestate application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.resourcestate.Application");

Ext.define("NOC.main.resourcestate.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.resourcestate.Model",
    "NOC.main.resourcestate.LookupField",
  ],
  model: "NOC.main.resourcestate.Model",
  search: true,
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
    },
    {
      text: __("Active"),
      dataIndex: "is_active",
      renderer: NOC.render.Bool,
      width: 70,
    },
    {
      text: __("Starting"),
      dataIndex: "is_starting",
      renderer: NOC.render.Bool,
      width: 70,
    },
    {
      text: __("Default"),
      dataIndex: "is_default",
      renderer: NOC.render.Bool,
      width: 70,
    },
    {
      text: __("Provisioned"),
      dataIndex: "is_provisioned",
      renderer: NOC.render.Bool,
      width: 70,
    },
    {
      text: __("Description"),
      dataIndex: "description",
      flex: 1,
    },
    {
      text: __("Step to"),
      dataIndex: "step_to",
      renderer: NOC.render.Lookup("step_to"),
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
      name: "description",
      xtype: "textarea",
      fieldLabel: __("Description"),
      allowBlank: true,
      anchor: "100%",
    },
    {
      name: "is_active",
      xtype: "checkboxfield",
      boxLabel: __("Active"),
      allowBlank: false,
    },
    {
      name: "is_starting",
      xtype: "checkboxfield",
      boxLabel: __("Starting"),
      allowBlank: false,
    },
    {
      name: "is_default",
      xtype: "checkboxfield",
      boxLabel: __("Default"),
      allowBlank: false,
    },
    {
      name: "is_provisioned",
      xtype: "checkboxfield",
      boxLabel: __("Provisioned"),
      allowBlank: false,
    },
    {
      name: "step_to",
      xtype: "main.resourcestate.LookupField",
      fieldLabel: __("Step to"),
      allowBlank: true,
    },
  ],
});
