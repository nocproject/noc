//---------------------------------------------------------------------
// inv.inv SensorPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.crossing.CrossingPanel");

Ext.define("NOC.inv.inv.plugins.crossing.CrossingPanel", {
  extend: "Ext.panel.Panel",
  title: __("Crossing"),
  closable: false,
  layout: "fit",
  requires: [
    "Ext.ux.form.GridField",
  ],
  initComponent: function(){
    var me = this;

    me.gridField = Ext.create({
      xtype: "gridfield",
      columns: [
        {
          dataIndex: "input",
          text: __("Input"),
          width: 150,
        },
        {
          dataIndex: "input_discriminator",
          text: __("Input Discriminator"),
          flex: 1,
        },
        {
          dataIndex: "output",
          text: __("Output"),
          width: 150,
        },
        {
          dataIndex: "output_discriminator",
          text: __("Output Discriminator"),
          flex: 1,
        },
        {
          dataIndex: "gain_db",
          text: __("Gain (dB)"),
          width: 75,
        },
      ],
    });
    Ext.apply(me, {
      items: [
        me.gridField,
      ],
    });
    me.callParent();
  },
  //
  preview: function(data){
    var me = this;
    me.currentId = data.id;
    me.gridField.store.loadData(data.data)
  },
});
