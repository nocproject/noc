//---------------------------------------------------------------------
// inv.inv PConf Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.pconf.PConfPanel");

Ext.define("NOC.inv.inv.plugins.pconf.PConfPanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.pconf.PConfModel",
    "NOC.inv.inv.plugins.pconf.Controller",
    "NOC.inv.inv.plugins.pconf.PConfEditPlugin",
  ],
  title: __("Config"),
  closable: false,
  layout: "fit",
  viewModel: {
    stores: {
      gridStore: {
        model: "NOC.inv.inv.plugins.pconf.PConfModel",
        listeners: {
          datachanged: "onDataChanged",
        },
        filters: [{
          property: "name",
          value: "{searchText}",
          anyMatch: true,
          caseSensitive: false,
        }, {
          property: "table",
          value: "{tabType}",
        }],
      },
    },
    data: {
      searchText: "",
      tabType: 1,
      totalCount: 0,
    },
  },
  controller: "pconf",
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
    {
      xtype: "combo",
      itemId: "tabType",
      store: [
        [1, "Info"],
        [2, "Status"],
        [3, "Config"],
        [4, "Thresholds"],
        [5, "Metrics"],
      ],
      queryMode: "local",
      displayField: "text",
      valueField: "value",
      bind: {
        value: "{tabType}",
      },
      value: 1,
      editable: false,
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
      autoScroll: true,
      stateful: true,
      bind: {
        store: "{gridStore}",
      },
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 250,
        },
        {
          text: __("Value"),
          dataIndex: "value",
          editor: {
            xtype: "textfield",
          },
          width: 200,
          renderer: function(value, metaData, record){
            var displayValue = value;
            if(record.get("type") === "enum"){
              var options = record.get("options") || [],
                option = options.find(opt => opt.id === value);
              displayValue = option ? option.label : value;
            }
            if(record.get("read_only")){
              displayValue = "<i class='fas fa fa-lock' style='padding-right: 4px;' title='" + __("Read only") + "'></i>" + displayValue;
            }
            return displayValue;
          },
        },
        {
          text: __("Units"),
          dataIndex: "units",
          width: 50,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
      ],
      plugins: [
        {
          ptype: "valueedit",
          clicksToEdit: 1,
        },
      ],
      listeners: {
        valuechanged: "onValueChanged",
      },
    },
  ],
  //
  preview: function(data){
    var me = this;
    me.currentId = data.id;
    me.getViewModel().get("gridStore").loadData(data.conf);
  },
});
