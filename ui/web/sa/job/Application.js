//---------------------------------------------------------------------
// sa.job application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.job.Application");

Ext.define("NOC.sa.job.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.sa.job.Model",
  ],
  model: "NOC.sa.job.Model",
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
        {
          text: __("Action"),
          dataIndex: "action",
          width: 100,
        },
        {
          text: __("Status"),
          dataIndex: "status",
          width: 150,
          renderer: NOC.render.JobStatus,
        },
      ],

      fields: [
      ],
    });
    me.callParent();
  },
});