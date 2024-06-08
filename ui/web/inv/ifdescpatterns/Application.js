//---------------------------------------------------------------------
// inv.ifdescpatterns application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.ifdescpatterns.Application");

Ext.define("NOC.inv.ifdescpatterns.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.inv.ifdescpatterns.Model",
  ],
  model: "NOC.inv.ifdescpatterns.Model",
  search: true,

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
          allowBlank: false,
          uiStyle: "medium",
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "resolve_remote_port_by_object",
          xtype: "checkbox",
          fieldLabel: __("Use object as Port Token"),
          allowBlank: true,
          renderer: NOC.render.Bool,
          tooltip: __('If checked discovery try find port by object_id (Hostname, Address, Name) contains in description'),
          listeners: {
            render: me.addTooltip,
          },
        },
        {
          name: "patterns",
          xtype: "gridfield",
          fieldLabel: __("Patterns"),
          columns: [
            {
              text: __("Active"),
              dataIndex: "is_active",
              editor: "checkbox",
              width: 50,
              renderer: NOC.render.Bool,
            },
            {
              text: __("Pattern"),
              dataIndex: "pattern",
              editor: "textfield",
              flex: 1,
            },
          ],
        },
      ],
    });
    me.callParent();
  },
});