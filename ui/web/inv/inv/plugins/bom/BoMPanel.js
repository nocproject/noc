//---------------------------------------------------------------------
// inv.inv BoM Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.bom.BoMPanel");

Ext.define("NOC.inv.inv.plugins.bom.BoMPanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.bom.BoMModel",
    "NOC.inv.inv.plugins.bom.Controller",
  ],
  title: __("BoM"),
  closable: false,
  controller: "bom",
  layout: "fit",
  viewModel: {
    stores: {
      gridStore: {
        model: "NOC.inv.inv.plugins.bom.BoMModel",
        sorters: [
          {property: "model", direction: "ASC"},
        ],
        listeners: {
          datachanged: "onDataChanged",
          beforeload: "onBeforeStoreLoad",
        },
      },
    },
    data: {
      searchText: "",
      totalCount: 0,
      currentId: undefined,
    },
  },
  tbar: [
    {
      glyph: NOC.glyph.refresh,
      tooltip: __("Reload"),
      handler: "onReload",
    },
    {
      xtype: "textfield",
      itemId: "searchText",
      emptyText: __("Search..."),
      width: 400,
      bind: {
        value: "{searchText}",
      },
      listeners: {
        change: function(field, newValue){
          var trigger = field.getTrigger("clear");
          if(newValue){
            trigger.show();
          } else{
            trigger.hide();
          }
        },
      },
      triggers: {
        clear: {
          cls: "x-form-clear-trigger",
          hidden: true,
          handler: function(field){
            field.setValue("");
            var grid = field.up("panel").down("gridpanel"),
              store = grid.getStore();
            store.clearFilter();
            field.getTrigger("clear").hide();
          },
        },
      },
    },
    "->",
    {
      xtype: "tbtext",
      bind: {
        html: __("Total") + ": {totalCount}",
      },
    },
  ],
  items: [
    {
      xtype: "gridpanel",
      border: false,
      stateful: true,
      bind: {
        store: "{gridStore}",
      },
      features: [{
        ftype: "grouping",
      }],
      scrollable: "y",
      columns: [
        {
          text: __("Vendor"),
          dataIndex: "vendor",
          width: 150,
        },
        {
          text: __("Model"),
          dataIndex: "model",
          width: 250,
        },
        {
          text: __("Location"),
          dataIndex: "location",
          flex: 1,
        },
        {
          text: __("Serial"),
          dataIndex: "serial",
          width: 150,
        },
        {
          text: __("Asset#"),
          dataIndex: "asset_no",
          width: 150,
        },
      ],
    },
  ],
  initComponent: function(){
    var me = this;
    me.callParent();

    var store = me.getViewModel().getStore("gridStore"),
      filters = store.getFilters();

    store.setGroupField("vendor");
    me.getViewModel().bind({
      bindTo: {
        searchText: "{searchText}",
      },
      single: false,
    }, function(data){
      filters.remove("invBoMFilter");
      filters.add({
        id: "invBoMFilter",
        filterFn: function(record){
          var text = data.searchText.toLowerCase(),
            vendor = record.get("vendor").toLowerCase(),
            model = record.get("model").toLowerCase(),
            serial = record.get("serial").toLowerCase(),
            asset_no = record.get("asset_no").toLowerCase();
          return vendor.includes(text) ||
              model.includes(text) ||
              serial.includes(text) ||
              asset_no.includes(text);
        },
      });
    });
  },
  preview: function(data, objectId){
    var me = this,
      vm = me.getViewModel();
    if(Object.prototype.hasOwnProperty.call(data, "status") && !data.status){
      NOC.error(data.message);
      return
    }
    vm.set("currentId", objectId);
    vm.get("gridStore").loadData(data.data);
  },
});
