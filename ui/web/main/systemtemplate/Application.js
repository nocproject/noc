//---------------------------------------------------------------------
// main.systemtemplate application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.systemtemplate.Application");

Ext.define("NOC.main.systemtemplate.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.pyrule.Model",
    "NOC.main.template.LookupField",
  ],
  model: "NOC.main.systemtemplate.Model",
  search: true,
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
      flex: 1,
    },

    {
      text: __("Template"),
      dataIndex: "template",
      renderer: NOC.render.Lookup("template"),
      flex: 1,
    },
  ],
  fields: [
    {
      name: "name",
      xtype: "textfield",
      fieldLabel: __("Name"),
      allowBlank: false,
      width: 400,
    },
    {
      name: "description",
      xtype: "textareafield",
      fieldLabel: __("Description"),
      allowBlank: false,
      anchor: "100%",
    },
    {
      name: "template",
      xtype: "main.template.LookupField",
      fieldLabel: __("Template"),
      allowBlank: false,
      width: 400,
    },
  ],
  filters: [
  ],
});
