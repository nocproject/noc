//---------------------------------------------------------------------
// Link Register window
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.service.RegisterForm");

Ext.define("NOC.sa.service.RegisterForm", {
  extend: "Ext.Window",
  requires: [
    "NOC.core.ComboBox",
  ],
  autoShow: true,
  closable: true,
  maximizable: true,
  modal: true,
  layout: "fit",
  defaultListenerScope: true,
  title: __("Register Instance"),
  items: [
    {
      xtype: "form",
      padding: 4,
      defaults: {
        labelAlign: "left",
        labelWidth: 150,
        allowBlank: false,
      },
      items: [
        {
          xtype: "hidden",
          name: "service_id",
        },
        {
          xtype: "core.combo",
          fieldLabel: __("Type"),
          name: "type",
          editable: false,
          typeAhead: false,
          uiStyle: "medium-combo",
        },
        {
          xtype: "textfield",
          fieldLabel: __("Name"),
          name: "name",
        },
        {
          xtype: "textfield",
          fieldLabel: __("FQDN"),
          name: "FQDN",
        },
      ],
      buttons: [
        {
          text: __("Register"),
          formBind: true,
          handler: "buttonHandler",
        },
      ],
    },
  ],
  buttonHandler: function(){
    var data = this.down("form").getForm().getValues(),
      url = "/sal/service/" + data.service_id + "/register_instance/" + data.type + "/",
      params = {
        name: data.name,
        FQDN: data.FQDN,
      };
    this.request(url, params);
  },
  request: function(url, params){
    Ext.Ajax.request({
      url: url,
      method: "POST",
      jsonData: params,
      success: function(response){
        console.log(response);
      },
      failure: function(){
        console.log("Failed");
      },
    });
  },
});