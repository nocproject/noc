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
      },
    },
    data: {
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
      emptyText: __("Search..."),
      width: 400,
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
      listeners: {
        change: function(field, newValue){
          var grid = field.up("panel").down("gridpanel"),
            store = grid.getStore();
          
          store.clearFilter();
          store.filterBy(function(record){
            return record.get("name").toLowerCase().includes(newValue.toLowerCase());
          });
          field.getTrigger("clear")[newValue.length > 0 ? "show" : "hide"]();
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
          editor: "textfield",
          width: 150,
          renderer: function(value, metaData, record){
            if(record.get("type") === "enum"){
              var options = record.get("options") || [];
              var option = options.find(opt => opt.id === value);
              return option ? option.label : value;
            }
            return value;
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
        Ext.create("Ext.grid.plugin.CellEditing", {
          clicksToEdit: 1,
          listeners: {
            beforeedit: function(editor, context){
              var record = context.record,
                column = context.column;
                    
              if(column.dataIndex === "value"){
                if(record.get("type") === "enum"){
                  column.setEditor({
                    xtype: "combobox",
                    store: {
                      fields: ["id", "label"],
                      data: record.get("options") || [],
                    },
                    valueField: "id",
                    displayField: "label",
                    queryMode: "local",
                  });
                } else{
                  column.setEditor({
                    xtype: "textfield",
                  });
                }
              }
            },
          },
        }),
      ],
    },
  ],
  //
  preview: function(data){
    var me = this;
    me.currentId = data.id;
    me.getViewModel().get("gridStore").loadData(data.conf);
  },
});
