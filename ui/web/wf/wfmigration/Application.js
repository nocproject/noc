//---------------------------------------------------------------------
// wf.wfmigration application
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.wf.wfmigration.Application");

Ext.define("NOC.wf.wfmigration.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.wf.wfmigration.Model",
    "NOC.wf.state.LookupField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.wf.wfmigration.Model",
  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 200,
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
          name: "migrations",
          xtype: "gridfield",
          columns: [
            {
              text: __("Active"),
              dataIndex: "is_active",
              editor: "checkbox",
              width: 50,
              renderer: NOC.render.Bool,
            },
            {
              text: __("From State"),
              dataIndex: "from_state",
              editor: "wf.state.LookupField",
              width: 150,
              renderer: NOC.render.Lookup("from_state"),
            },
            {
              text: __("To State"),
              dataIndex: "to_state",
              editor: "wf.state.LookupField",
              width: 150,
              renderer: NOC.render.Lookup("to_state"),
            },
            {
              text: __("Description"),
              dataIndex: "description",
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
