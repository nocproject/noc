//---------------------------------------------------------------------
// NOC.core SubscriptionPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.SubscriptionPanel");

Ext.define("NOC.core.SubscriptionPanel", {
  extend: "NOC.core.ApplicationPanel",
  alias: "widget.core.subscriptionpanel",
  requires: [
    "NOC.core.plugins.SubscriptionModalEditing",
  ],
  urlSuffix: "subscription",
  viewModel: {
    data: {
      isSelected: false,
    },
  },
  defaultListenerScope: true,
  items: [
    {
      xtype: "grid",
      autoScroll: true,
      selModel: {
        allowDeselect: true,
      },
      store: Ext.create("Ext.data.Store", {
        fields: [
          "source", 
          "notification_group", 
          "users", 
          "crm_users", 
          "me_suppress", 
          "me_subscribe",
        ],
      }),
      plugins: [
        {
          ptype: "subscriptionmodalediting",
          clicksToEdit: 1,
          autoCancel: false,
        },
      ],
      tbar: [
        {
          text: __("Close"),
          tooltip: __("Close without saving"),
          glyph: NOC.glyph.arrow_left,
          handler: "onClose",
        },
        "|",
        {
          text: __("Add"),
          tooltip: __("Add me to this subscription"),
          bind: {
            disabled: "{!isSelected}",
          },
          handler: "onAddMe",
        },
        {
          text: __("Remove"),
          tooltip: __("Remove me to this subscription"),
          bind: {
            disabled: "{!isSelected}",
          },
          handler: "onRemoveMe",
        },
        {
          text: __("Suppress"),
          tooltip: __("Suppress me to this subscription"),
          bind: {
            disabled: "{!isSelected}",
          },
          handler: "onSuppressMe",
        },
      ],
      columns: [
        {
          text: __("Source"),
          dataIndex: "source",
        },
        {
          text: __("Notification Group"),
          dataIndex: "notification_group",
          renderer: NOC.render.Lookup("notification_group"),
        },
        {
          text: __("Users"),
          dataIndex: "users",
          renderer: function(value){
            return value.map(function(user){
              return user.user__label;
            }).join(",");
          },
        },
        {
          text: __("CRM Users (Contacts)"),
          dataIndex: "crm_users",
          renderer: function(value){
            return value.map(function(user){
              return user.user__label;
            }).join(",");
          },
        },
        {
          text: __("Suppress"),
          dataIndex: "me_suppress",
          renderer: NOC.render.Bool,
        },
        {
          text: __("Subscribe"),
          dataIndex: "me_subscribe",
          renderer: NOC.render.Bool,
        },
      ],
      listeners: {
        selectionchange: "onSelectionChange",
      },
    },
  ],
  //
  load: function(appId, recordId, showOnClose){
    this.appId = appId;
    this.currentRecordId = recordId;
    this.showOnClose = showOnClose;
    this.request(
      this.makeUrl(appId, recordId, "object_subscription"),
      "GET",
      function(self, data){
        var store = self.down("grid").getStore();
        store.loadData(data);
      },
    );
  },
  //
  makeUrl: function(appId, recordId, suffix){ 
    var prefix = appId.replace(/\./g, "/");
    return Ext.String.format("/{0}/{1}/{2}/", prefix, recordId, suffix);
  },
  //
  request: function(url, method, successCallback){
    Ext.Ajax.request({
      url: url,
      method: method,
      scope: this,
      success: function(response){
        var result = Ext.decode(response.responseText);
        if(method === "GET"){
          successCallback(this, result);
          return;
        }
        if(result.success){
          successCallback(this, result.data);
        } else{
          NOC.error("Error " + " : " + result.message || "Operation failed");
        }
      },
      failure: function(response){
        NOC.error("Request failed: ", response);
      },
    });
  },
  // handlers
  //
  onClose: function(){
    var app = this.up("[appId]");
    app.showItem(app[this.showOnClose]);
    Ext.History.setHash(app.appId);
    app.reloadStore();
  },
  //
  onAddMe: function(){
    this.subscribe("subscribe");
  },
  //
  onRemoveMe: function(){
    this.subscribe("unsubscribe");
  },
  //
  onSuppressMe: function(){
    this.subscribe("suppress");
  },
  subscribe: function(action){
    var notificationGroup = this.down("grid").selection.data.notification_group,
      prefix = `object_subscription/${notificationGroup}/${action}`,
      url = this.makeUrl(this.appId, this.currentId, prefix);
    console.log("subscribe :", url);
  },
  //
  onSelectionChange: function(grid, selected){
    var vm = this.getViewModel();
    vm.set("isSelected", selected.length > 0);
  },
});