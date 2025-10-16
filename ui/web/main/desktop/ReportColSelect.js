//---------------------------------------------------------------------
// main.desktop.report application
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.ReportColSelect");

Ext.define("NOC.main.desktop.ReportColSelect", {
  extend: "Ext.form.FieldContainer",
  alias: "widget.reportcolumnselect",
  mixins: {
    field: "Ext.form.field.Field",
  },
  requires: [
  ],
  initComponent: function(){
    var me = this;

    me.grid = Ext.create("Ext.grid.Panel", {
      layout: "fit",
      columns: [
        {
          text: __("Active"),
          dataIndex: "is_active",
          width: 25,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Field"),
          dataIndex: "label",
          flex: 1,
        },
      ],
      store: {
        fields: [
          "id",
          "label",
          {
            name: "is_active",
            type: "boolean",
          },
        ],
        data: me.storeData,
      },
      listeners: {
        rowdblclick: me.toggle,
      },
    });
    Ext.apply(me, {
      items: [
        me.grid,
      ],
    })

    me.callParent();
  },
  getValue: function(){
    var me = this,
      selectedFields = Ext.Array.filter(me.grid.getStore().getData().items, function(field){return field.get("is_active");});

    return Ext.Array.map(selectedFields, function(field){return field.id;}).join(",");
  },
  toggle: function(self, record){
    record.set("is_active", !record.get("is_active"));
  },
});