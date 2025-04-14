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
  defaultListenerScope: true,
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
        hideTriggerUpdate: true,
        hideTriggerCreate: true,
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
          handler: "buttonBindHandler",
        },
        {
          text: __("Unbind"),
          handler: "buttonResetHandler",
        },
        {
          text: __("Reset"),
          handler: "resetFormHandler",
        },
        {
          text: __("Close"),
          handler: function(){
            this.up("window").close();
          }, 
        },
      ],
    },
  ],
  buttonBindHandler: function(){
    this.buttonHandler("bind")
  },
  buttonResetHandler: function(){
    this.buttonHandler("unbind");
  },
  buttonHandler: function(method){
    var data = this.down("form").getForm().getValues(),
      url = "/sa/service/" + data.service_id + "/instance/" + data.instance_id + "/" + method,
      params = {resources: [data.resources]};
    if(method !== "bind"){
      url += "/resources/";
      params = undefined;
    }
    this.request(url, params, method);
  },
  request: function(url, params, method){
    Ext.Ajax.request({
      url: url,
      method: "PUT",
      jsonData: params,
      success: function(response){
        var result = Ext.decode(response.responseText);
        if(result.success){
          this.instanceRecord.set("resources", result.data.resources);
          this.instanceRecord.commit();
          NOC.info(__("Resource") + " " + method + " " + __("successfully"));
          this.close();
        } else{
          NOC.error(__("Error") + " : " + result.message || __("Operation failed"));
        }
      },
      failure: function(){
        NOC.error("Error : Server error occurred");
      },
      scope: this,
    });
  },
  resetFormHandler: function(){
    this.down("form").getForm().reset();
    this.center();
  },
});