//---------------------------------------------------------------------
// main.metricstream application
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.metricstream.Application");

Ext.define("NOC.main.metricstream.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.metricstream.Model",
    "NOC.pm.metricscope.LookupField",
    "NOC.pm.metrictype.LookupField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.main.metricstream.Model",
  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Scope"),
          dataIndex: "scope",
          width: 200,
          renderer: NOC.render.Lookup("scope"),
        },
        {
          text: __("Active"),
          dataIndex: "is_active",
          width: 25,
          renderer: NOC.render.Bool,
        },
      ],

      fields: [
        {
          name: "scope",
          xtype: "pm.metricscope.LookupField",
          fieldLabel: __("Scope"),
          allowBlank: false,
        },
        {
          name: "is_active",
          xtype: "checkbox",
          boxLabel: __("Active"),
        },
        {
          name: "fields",
          xtype: "gridfield",
          fieldLabel: __("Fields"),
          columns: [
            {
              text: __("Metric Type"),
              dataIndex: "metric_type",
              width: 150,
              editor: {
                xtype: "pm.metrictype.LookupField",
              },
              renderer: NOC.render.Lookup("metric_type"),
            },
            {
              dataIndex: "external_alias",
              text: __("External Alias"),
              width: 150,
              editor: "textfield",
            },
            {
              text: __("Expose MX"),
              dataIndex: "expose_mx",
              width: 50,
              renderer: NOC.render.Bool,
              editor: "checkbox",
            },
            {
              text: __("Expose Condition"),
              dataIndex: "expose_condition",
              width: 50,
              renderer: NOC.render.Bool,
              editor: "checkbox",
            },
          ],

        },
      ],
    });
    me.callParent();
  },
  filters: [
    {
      title: __("By Active"),
      name: "is_active",
      ftype: "boolean",
    },
  ],
});
