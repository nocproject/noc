//---------------------------------------------------------------------
// inv.inv PConf Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.pconf.PConfPanel");

Ext.define("NOC.inv.inv.plugins.pconf.PConfPanel", {
  extend: "Ext.panel.Panel",
  config: {
    status: {
      "?": {
        color: "#7f8c8d",
        glyph: "question",
      },
      c: {
        color: "#c0392b",
        glyph: "check-circle",
      },
      w: {
        color: "#e67e22",
        glyph: "exclamation-circle",
      },
      o: {
        color: "#16a085",
        glyph: "exclamation-triangle",
      },
    },
  },
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
        filters: [
          {
            property: "name",
            value: "{searchText}",
            anyMatch: true,
            caseSensitive: false,
          },
          {
            property: "table",
            value: "{tabType}",
          },
        ],
      },
    },
    data: {
      searchText: "",
      status: null,
      statusDisabled: true,
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
      width: 300,
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
      fieldLabel: __("Mode"),
      allowBlank: false,
      labelAlign: "right",
      bind: {
        value: "{tabType}",
      },
      value: 1,
      editable: false,
      listeners: {
        select: "onTabTypeChange",
      },
    },
    {
      xtype: "segmentedbutton",
      itemId: "statusFilter",
      allowDepress: true,
      bind: {
        disabled: "{statusDisabled}",
        value: "{status}",
      },
      items: [
        {
          tooltip: __("Unknown"),
          toggleGroup: "status",
          value: "?",
          listeners: {
            afterrender: "onButtonRender",
          },
        },
        {
          tooltip: __("Ok"),
          toggleGroup: "status",
          value: "o",
          listeners: {
            afterrender: "onButtonRender",
          },
        },
        {
          tooltip: __("Warning"),
          toggleGroup: "status",
          value: "w",
          listeners: {
            afterrender: "onButtonRender",
          },
        },
        {
          tooltip: __("Critical"),
          toggleGroup: "status",
          value: "c",
          listeners: {
            afterrender: "onButtonRender",
          },
        },
      ],
      listeners: {
        toggle: "onStatusChange",
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
          renderer: "valueRenderer",
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
    if(Object.prototype.hasOwnProperty.call(data, "status") && !data.status){
      NOC.error(data.message);
      return
    }
    me.currentId = data.id;
    me.getViewModel().get("gridStore").loadData(data.conf);
  },
});
