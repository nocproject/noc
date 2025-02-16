//---------------------------------------------------------------------
// Link Resources window
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.service.ResourceLinkForm");

Ext.define("NOC.sa.service.ResourceLinkForm", {
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
      defaults: {
        labelAlign: "left",
        labelWidth: 150,
        allowBlank: false,
        xtype: "core.combo",
        uiStyle: "medium-combo",
      },
      items: [
        {
          xtype: "hidden",
          name: "service_id",
        },
        {
          xtype: "hidden",
          name: "instance_id",
        },
        {
          xtype: "radiogroup",
          fieldLabel: __("Type"),
          layout: "hbox",
          items: [
            {
              boxLabel: __("Interface"),
              name: "type",
              inputValue: "interface",
              checked: true,
              margin: "0 10 0 0", 
            },
            {
              boxLabel: __("Subinterface"),
              name: "type",
              inputValue: "subinterface",
            },
          ],
          listeners: {
            change: function(field, newValue){
              var form = this.up("form"),
                resourceCombo = form.down("[name=resources]"),
                resourceUrl = resourceCombo.getStore().getProxy().getUrl();
              if(newValue.type === "interface"){
                resourceUrl = resourceUrl.replace("subinterface", "interface");
              } else{
                resourceUrl = resourceUrl.replace("interface", "subinterface");
              }
              resourceCombo.getStore().getProxy().setUrl(resourceUrl)
              resourceCombo.reset();
            },
          },
        },
        {
          fieldLabel: __("Managed Object"),
          name: "managed_id",
          restUrl: "/sa/managedobject/lookup/",
          listeners: {
            change: function(field, newValue){
              var form = this.up("form"),
                resourceCombo = form.down("[name=resources]");
              resourceCombo.getStore().getProxy().setExtraParams({
                managed_object: newValue,
              });
              resourceCombo.reset();
            },
          },
        },
        {
          fieldLabel: __("Resource"),
          name: "resources",
          valueField: "resource",
          displayField: "resource__label",
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
          handler: function(){
            var data = this.up("form").getForm().getValues();
            console.log("reset", data);
          },
        },
      ],
    },
  ],
});