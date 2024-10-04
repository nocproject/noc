//---------------------------------------------------------------------
// sa.managedobjectselector ObjectsPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintenance.maintenance.ObjectsPanel");

Ext.define("NOC.maintenance.maintenance.ObjectsPanel", {
  extend: "Ext.grid.Panel",
  requires: [
    "NOC.maintenance.maintenance.ObjectsModel",
    "NOC.maintenance.maintenance.ObjectsStore",
    "NOC.core.label.LabelField",
  ],
  mixins: [
    "NOC.core.mixins.Export",
  ],
  app: null,
  autoScroll: true,
  stateful: true,
  autoDestroy: true,
  stateId: "sa.managedobjectselector-objects",
  loadMask: true,
  defaultListenerScope: true,
  store: {
    type: "maintenance.objects",
  },
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
      width: 200,
    },
    {
      text: __("Managed"),
      dataIndex: "is_managed",
      renderer: NOC.render.Bool,
      width: 50,
    },
    {
      text: __("Profile"),
      dataIndex: "profile",
      width: 100,
    },
    {
      text: __("Address"),
      dataIndex: "address",
      width: 100,
    },
    {
      text: __("Description"),
      dataIndex: "description",
      flex: 1,
    },
    {
      text: __("Labels"),
      dataIndex: "labels",
      renderer: NOC.render.LabelField,
      width: 150,
    },
  ],
  dockedItems: [
    {
      xtype: "toolbar",
      dock: "top",
      items: [
        {
          text: __("Close"),
          glyph: NOC.glyph.arrow_left,
          handler: "onClose",
        },
        {
          tooltip: __("Export"),
          text: __("Export"),
          glyph: NOC.glyph.arrow_down,
          handler: "onExport",

        },
        "->",
        {
          xtype: "displayfield",
          fieldLabel: __("Total"),
          name: "total",
          value: __("loading..."),
        },
      ],
    },
  ],

  preview: function(record, backItem){
    var me = this,
      bi = backItem === undefined ? me.backItem : backItem,
      store = me.getStore();

    store.getProxy().setUrl("/maintenance/maintenance/" + record.get("id") + "/objects/");
    store.load({
      scope: me,
      callback: function(){
        me.down("[name=total]").setValue(store.getTotalCount());
      },
    });
    me.currentRecord = record;
    me.backItem = bi;
  },

  onClose: function(){
    var me = this;
    me.app.showItem(me.backItem);
  },

  onExport: function(){
    var me = this;
    me.save(me, 'affected.csv');
  },
});
