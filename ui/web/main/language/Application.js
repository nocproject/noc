//---------------------------------------------------------------------
// main.language application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.language.Application");

Ext.define("NOC.main.language.Application", {
  extend: "NOC.core.ModelApplication",
  requires: ["NOC.main.language.Model"],
    
  model: "NOC.main.language.Model",
  search: true,
    
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
    },
    {
      text: __("Native Name"),
      dataIndex: "native_name",
    },
    {
      text: __("Active"),
      dataIndex: "is_active",
      renderer: NOC.render.Bool,
    },
  ],
    
  fields: [
    {
      xtype: "textfield",
      fieldLabel: __("Name"),
      name: "name",
      allowBlank: false,
    },

    {
      xtype: "textfield",
      fieldLabel: __("Native Name"),
      name: "native_name",
      allowBlank: false,
    },
        
    {
      xtype: "checkboxfield",
      boxLabel: __("Is Active"),
      name: "is_active",
      inputValue: true,
    },
  ],

  filters: [
    {
      title: __("By Is Active"),
      ftype: "boolean",
      name: "is_active",
    },
  ],
});
