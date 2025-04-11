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
      addDisabled: true,
      removeDisabled: true,
    },
  },
  defaultListenerScope: true,
  items: [
    {
      xtype: "grid",
      autoScroll: true,
      forceFit: true,
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
            disabled: "{addDisabled}",
          },
          handler: "onAddMe",
        },
        {
          text: __("Remove"),
          tooltip: __("Remove me to this subscription"),
          bind: {
            disabled: "{removeDisabled}",
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
          flex: 0.5,
        },
        {
          text: __("Notification Group"),
          dataIndex: "notification_group",
          flex: 1,
          renderer: NOC.render.Lookup("notification_group"),
        },
        {
          text: __("Users"),
          dataIndex: "users",
          flex: 4,
          lookupUrl: "/aaa/user/lookup/",
          renderer: "userRenderer",
        },
        {
          text: __("CRM Users (Contacts)"),
          dataIndex: "crm_users",
          flex: 4,
          lookupUrl: "/crm/subscriber/lookup/",
          renderer: "userRenderer",
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
    if(this.rendered && !this.destroyed){
      this.mask(__("Updating ..."));
    }
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
      callback: function(){
        if(this.rendered && !this.destroyed){
          this.unmask();
        }
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
      url = this.makeUrl(this.appId, this.currentRecordId, prefix);
    this.request(
      url,
      "POST",
      function(self, data){
        var grid = self.down("grid");
        grid.selection.set(data);
        grid.selection.commit();
        self.onSelectionChange(grid, [grid.selection]);
        NOC.info(__("Operation completed"));
      },
    );
  },
  //
  onSelectionChange: function(grid, selected){
    var vm = this.getViewModel(),
      isSelected = selected.length > 0;
    if(isSelected){
      var record = selected[0].data;
      vm.set({
        isSelected: record.me_suppress,
        addDisabled: record.me_subscribe,
        removeDisabled: !record.me_subscribe,
      });
    }
    else{
      vm.set("isSelected", false);
      vm.set("addDisabled", true);
      vm.set("removeDisabled", true);
    }
  },
  //
  userRenderer: function(value, metaData, record){
    var icon = "<i class='fa fa-pencil' style='padding-right: 4px;'></i>";
    metaData.tdStyle = "cursor: pointer;";
    if(!record.get("allow_edit")){
      metaData.tdStyle = "cursor: not-allowed;";
      icon = "<i class='fa fa-lock' style='padding-right: 4px;' title='" + __("Read only") + "'></i>";
    }

    return icon + value.map(function(user){
      return user.user__label;
    }).join(",");
  },
});