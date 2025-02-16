//---------------------------------------------------------------------
// Link Address window
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.service.AddressesLinkForm");

Ext.define("NOC.sa.service.AddressesLinkForm", {
  extend: "Ext.Window",
  requires: [
    "NOC.core.ComboBox",
  ],
  autoShow: true,
  closable: true,
  maximizable: true,
  modal: true,
  scrollable: true,
  layout: "fit",
  items: [
    {
      xtype: "form",
      padding: 4,
      items: [
        {
          xtype: "hidden",
          name: "service_id",
        },
        {
          xtype: "hidden",
          name: "instance_id",
        },
      ],
      buttons: [
        {
          text: __("Bind"),
          formBind: true,
          handler: function(){
            var data = this.up("form").getForm().getValues();
            console.log("bind", data);
          },
        },
        {
          text: __("Reset"),
          formBind: true,
          handler: function(){
            var data = this.up("form").getForm().getValues();
            console.log("reset", data);
          },
        },
      ],
    },
  ],
});