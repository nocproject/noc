//---------------------------------------------------------------------
// Link ManagedObject window
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.service.ManagedObjectLinkForm");

Ext.define("NOC.sa.service.ManagedObjectLinkForm", {
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
          fieldLabel: __("Managed Object"),
          labelAlign: "left",
          labelWidth: 150,
          name: "managed_id",
          allowBlank: false,
          xtype: "core.combo",
          restUrl: "/sa/managedobject/lookup/",
          uiStyle: "medium-combo",
        },
      ],
      buttons: [
        {
          text: __("Bind"),
          formBind: true,
          handler: "buttonBindHandler",
        },
        {
          text: __("Reset"),
          handler: "buttonResetHandler",
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
      params = {managed_object: data.managed_id};
    if(method !== "bind"){
      url += "/managed_object/";
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
          this.instanceRecord.set("managed_object", result.data.managed_object);
          this.instanceRecord.set("managed_object__label", result.data.managed_object__label);
          this.instanceRecord.commit();
          NOC.info(__("Success Managed object") + " " + method + " " + __("successfully"));
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
});