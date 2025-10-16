//---------------------------------------------------------------------
// maintenance.maintenancetype application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintenance.maintenancetype.Application");

Ext.define("NOC.maintenance.maintenancetype.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.maintenance.maintenancetype.Model",
  ],
  model: "NOC.maintenance.maintenancetype.Model",
  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 150,
        },
        {
          text: __("Suppress"),
          dataIndex: "suppress_alarms",
          width: 75,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          uiStyle: "medium",
          allowBlank: false,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          uiStyle: "extra",
          allowBlank: true,
        },
        {
          name: "suppress_alarms",
          xtype: "checkbox",
          boxLabel: __("Suppress Alarms"),
        },
        {
          name: "card_template",
          xtype: "textfield",
          fieldLabel: __("Card Template"),
          allowBlank: true,
        },
      ],
    });
    me.callParent();
  },
});
