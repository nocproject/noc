//---------------------------------------------------------------------
// Integration fieldset
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.IntegrationField");
Ext.define("NOC.core.IntegrationField", {
  extend: "Ext.form.FieldSet",
  xtype: "noc.integrationfield",
  layout: "hbox",
  title: __("Integration"),
  defaults: {
    padding: 4,
    labelAlign: "left",
  },
  items: [
    {
      name: "remote_system",
      xtype: "main.remotesystem.LookupField",
      fieldLabel: __("Remote System"),
      labelWidth: 150,
      allowBlank: true,
    },
    {
      name: "remote_id",
      xtype: "textfield",
      fieldLabel: __("Remote ID"),
      labelWidth: 150,
      width: 330,
      allowBlank: true,
    },
    {
      name: "bi_id",
      xtype: "displayfield",
      fieldLabel: __("BI ID."),
      labelWidth: 50,
      allowBlank: true,
      uiStyle: "medium",
      renderer: function(value){
        return value + NOC.clipboardIcon(value);
      },
    },
  ],
});