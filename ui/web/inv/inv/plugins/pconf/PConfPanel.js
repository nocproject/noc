//---------------------------------------------------------------------
// inv.inv PConf Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details

const {stat} = require("fs");

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
    "NOC.inv.inv.plugins.pconf.PConfController",
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
          // {
          // property: "table",
          // value: "{tabType}",
          // },
          // {
          //   property: "status",
          //   value: "{status}",
          // },
          // {
          // id: "groupFilter",
          // property: "group",
          // exactMatch: true,
          // value: "{groupParam}",
          // },
        ],
      },
      groupStore: {
        fields: ["id", "label"],
        data: [],
      },
      tableStore: {
        fields: ["id", "label"],
        data: [],
      },
    },
    data: {
      searchText: "",
      // status: "u",
      tabType: "",
      groupParam: "",
      totalCount: 0,
      currentId: null,
      icon: "<i class='fa fa-fw' style='padding-left:4px;width:16px;'></i>",
      mgmt_url: "",
    },
  },
  controller: "pconf",
  timer: undefined,
  listeners: {
    activate: "onActivate",
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
      queryMode: "local",
      displayField: "label",
      valueField: "id",
      editable: false,
      // fieldLabel: __("Mode"),
      // labelWidth: 130,
      // allowBlank: false,
      // labelAlign: "right",
      bind: {
        store: "{tableStore}",
        value: "{tabType}",
      },
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
      displayField: "label",
      valueField: "id",
      editable: false,
      // fieldLabel: __("Group"),
      // labelAlign: "right",
      listeners: {
        select: "onReload",
      },
    },
    {
      glyph: NOC.glyph.wrench,
      tooltip: __("Management console"),
      handler: "onMgmtClick",
      bind: {
        disabled: "{!mgmt_url}",
      },
    },
    // {
    //   xtype: "segmentedbutton",
    //   itemId: "statusFilter",
    //   allowDepress: false,
    //   bind: {
    //     value: "{status}",
    //   },
    //   items: [
    //     {
    //       tooltip: __("Unknown"),
    //       toggleGroup: "status",
    //       value: "u",
    //     },
    //     {
    //       tooltip: __("Ok"),
    //       toggleGroup: "status",
    //       value: "o",
    //     },
    //     {
    //       tooltip: __("Warning"),
    //       toggleGroup: "status",
    //       value: "w",
    //     },
    //     {
    //       tooltip: __("Critical"),
    //       toggleGroup: "status",
    //       value: "c",
    //     },
    //   ],
    //   listeners: {
    //     afterrender: "onButtonsRender",
    //     // toggle: "onStatusChange",
    //   },
    // },
    "->",
    {
      xtype: "tbtext",
      bind: {
        html: __("Total") + ": {totalCount}" + "{icon}",
      },
    },
  ],
  items: [
    {
      xtype: "gridpanel",
      border: false,
      autoScroll: true,
      stateful: true,
      stateId: "inv.inv-pconf-grid",
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
  preview: function(data, id){
    var vm = this.getViewModel(),
      gridStore = vm.getStore("gridStore"),
      groupStore = vm.getStore("groupStore"),
      tableStore = vm.getStore("tableStore"),
      // uniqueGroups = Ext.Array.map(Ext.Array.unique(Ext.Array.pluck(data.conf, "group")), function(obj){return {value: obj};}),
      firstTable = Ext.isEmpty(data.tables) ? __("no tables") : data.tables[0].id,
      firstGroup = Ext.isEmpty(data.groups) ? __("no groups") : data.groups[0].id;

    if(Ext.isEmpty(gridStore) || Ext.isEmpty(groupStore) || Ext.isEmpty(tableStore)){
      return;
    }
    if(Object.prototype.hasOwnProperty.call(data, "status") && !data.status){
      NOC.error(data.message);
      return
    }
    vm.set("currentId", id);
    groupStore.loadData(data.groups);
    tableStore.loadData(data.tables);
    gridStore.loadData(data.conf);
    vm.set("mgmt_url", data.mgmt_url || "");
    if(vm.get("tabType") === ""){
      vm.set("tabType", firstTable);
    }
    if(vm.get("groupParam") === ""){
      vm.set("groupParam", firstGroup);
    }
  },
  onDestroy: function(){
    if(this.timer){
      Ext.TaskManager.stop(this.timer);
    }
    this.callParent();
  },
});
