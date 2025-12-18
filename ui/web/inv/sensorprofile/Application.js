//---------------------------------------------------------------------
// inv.sensorprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.sensorprofile.Application");

Ext.define("NOC.inv.sensorprofile.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.tagfield.Tagfield",
    "NOC.core.label.LabelField",
    "NOC.core.ListFormField",
    "NOC.main.handler.LookupField",
    "NOC.inv.sensorprofile.Model",
    "NOC.pm.metrictype.LookupField",
    "NOC.wf.workflow.LookupField",
    "NOC.main.remotesystem.LookupField",
    "NOC.main.style.LookupField",
    "NOC.pm.measurementunits.LookupField"
  ],
  model: "NOC.inv.sensorprofile.Model",
  search: true,
  rowClassField: "row_class",

  initComponent: function() {
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          flex: 1
        },
        {
          text: __("Labels"),
          dataIndex: "labels",
          renderer: NOC.render.LabelField,
          width: 100
        }
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "medium"
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
          uiStyle: "extra"
        },
        {
          name: "workflow",
          xtype: "wf.workflow.LookupField",
          fieldLabel: __("WorkFlow"),
          allowBlank: true
        },
        {
          name: "style",
          xtype: "main.style.LookupField",
          fieldLabel: __("Style"),
          allowBlank: true
        },
        {
          name: "units",
          xtype: "pm.measurementunits.LookupField",
          fieldLabel: __("Sensor Measurement Units"),
          allowBlank: true
        },
        {
          name: "metric_type",
          xtype: "pm.metrictype.LookupField",
          fieldLabel: __("Metric Type"),
          allowBlank: true,
        },
        {
          name: "dynamic_classification_policy",
          xtype: "combobox",
          fieldLabel: __("Dynamic Classification Policy"),
          allowBlank: false,
          queryMode: "local",
          displayField: "label",
          valueField: "id",
          store: {
            fields: ["id", "label"],
            data: [
                {id: "D", label: "Disable"},
                {id: "R", label: "By Rule"},
            ]
          },
          defaultValue: "R",
          uiStyle: "medium"
        },
        {
          name: "enable_collect",
          xtype: "checkbox",
          boxLabel: __("Enable Collect"),
          allowBlank: true
        },
        {
          name: "collect_interval",
          xtype: "numberfield",
          fieldLabel: __("Collect interval"),
          allowBlank: true,
          uiStyle: "medium",
          minValue: 1,
          maxValue: 3600
        },
        {
          name: "bi_id",
          xtype: "displayfield",
          fieldLabel: __("BI ID"),
          allowBlank: true,
          uiStyle: "medium"
        },
        {
          name: "labels",
          xtype: "labelfield",
          fieldLabel: __("Labels"),
          allowBlank: true,
          query: {
            "enable_sensorprofile": true
          }
        },
        {
          name: "match_rules",
          xtype: "listform",
          fieldLabel: __("Match Rules"),
          items: [
              {
                name: "dynamic_order",
                xtype: "numberfield",
                fieldLabel: __("Dynamic Order"),
                allowBlank: true,
                defaultValue: 0,
                uiStyle: "small"
              },
            {
              name: "labels",
              xtype: "labelfield",
              fieldLabel: __("Match Labels"),
              allowBlank: true,
              isTree: true,
              filterProtected: false,
              pickerPosition: "down",
              uiStyle: "extra",
              query: {
                "allow_matched": true
              }
              },
            {
              xtype: "core.tagfield",
              url: "/inv/resourcegroup/lookup/",
              fieldLabel: __("Object Groups"),
              name: "resource_groups",
              allowBlank: true,
              uiStyle: "extra",
            },
            {
              name: "units",
              xtype: "pm.measurementunits.LookupField",
              fieldLabel: __("Match M Units"),
              allowBlank: true,
              uiStyle: "medium",
            },
            {
              name: "remote_system",
              xtype: "main.remotesystem.LookupField",
              fieldLabel: __("Remote System"),
              allowBlank: true,
            },
            {
              name: "name_pattern",
              xtype: "textfield",
              fieldLabel: __("Label Pattern"),
              allowBlank: true,
              uiStyle: "medium",
            },
          ],
        },
      ],
    });
    me.callParent();
  }
});
