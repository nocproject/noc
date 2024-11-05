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
      u: {
        color: "#7f8c8d",
        glyph: "question",
      },
      c: {
        color: "#c0392b",
        glyph: "exclamation-triangle",
      },
      w: {
        color: "#f1c40f",
        glyph: "exclamation-circle",
      },
      o: {
        color: "#16a085",
        glyph: "check-circle",
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
      groupStore: {
        fields: ["value"],
        data: [],
      },
    },
    data: {
      searchText: "",
      status: null,
      statusDisabled: {
        u: false,
        c: false,
        w: false,
        o: false,
      },
      tabType: 1,
      groupParam: __("All"),
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
      labelWidth: 130,
      allowBlank: false,
      labelAlign: "right",
      bind: {
        value: "{tabType}",
      },
      editable: false,
      listeners: {
        select: "onTabTypeChange",
      },
    },
    {
      xtype: "combo",
      itemId: "groupParam",
      bind: {
        store: "{groupStore}",
        value: "{groupParam}",
      },
      queryMode: "local",
      displayField: "value",
      valueField: "value",
      fieldLabel: __("Group"),
      labelAlign: "right",
      editable: false,
      listeners: {
        select: "onGroupParamChange",
      },
    },
    {
      xtype: "segmentedbutton",
      itemId: "statusFilter",
      allowDepress: true,
      bind: {
        value: "{status}",
      },
      items: [
        {
          tooltip: __("Unknown"),
          toggleGroup: "status",
          value: "u",
          bind: {
            disabled: "{statusDisabled.u}",
          },
          listeners: {
            afterrender: "onButtonRender",
          },
        },
        {
          tooltip: __("Ok"),
          toggleGroup: "status",
          value: "o",
          bind: {
            disabled: "{statusDisabled.o}",
          },
          listeners: {
            afterrender: "onButtonRender",
          },
        },
        {
          tooltip: __("Warning"),
          toggleGroup: "status",
          value: "w",
          bind: {
            disabled: "{statusDisabled.w}",
          },
          listeners: {
            afterrender: "onButtonRender",
          },
        },
        {
          tooltip: __("Critical"),
          toggleGroup: "status",
          value: "c",
          bind: {
            disabled: "{statusDisabled.c}",
          },
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
      emptyText: __("No data"),
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
        // {
        // text: __("Units"),
        // dataIndex: "units",
        // width: 50,
        // },
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
