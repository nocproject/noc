//---------------------------------------------------------------------
// inv.cpeprofile application
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.cpeprofile.Application");

Ext.define("NOC.inv.cpeprofile.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.label.LabelField",
    "NOC.core.ListFormField",
    "NOC.main.handler.LookupField",
    "NOC.inv.sensorprofile.Model",
    "NOC.wf.workflow.LookupField",
    "NOC.main.style.LookupField",
    "NOC.pm.metrictype.LookupField"
  ],
  model: "NOC.inv.cpeprofile.Model",
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
          name: "metrics_default_interval",
          xtype: "numberfield",
          fieldLabel: __("Metric Default interval"),
          allowBlank: true,
          uiStyle: "medium",
          minValue: 0,
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
            name: "metrics",
            xtype: "gridfield",
            fieldLabel: __("Metrics"),
            minWidth: me.formMinWidth,
            maxWidth: me.formMaxWidth,
            columns: [
                {
                    text: __("Metric Type"),
                    dataIndex: "metric_type",
                    width: 250,
                    editor: {
                        xtype: "pm.metrictype.LookupField"
                    },
                    renderer: NOC.render.Lookup("metric_type")
                },
                {
                    text: __("Stored"),
                    dataIndex: "is_stored",
                    width: 50,
                    renderer: NOC.render.Bool,
                    editor: "checkbox"
                },
                {
                    text: __("Interval"),
                    dataIndex: "interval",
                    editor: {
                        xtype: "numberfield",
                        minValue: 0,
                        defaultValue: 300,
                    }
                }
            ]
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
              allowBlank: false,
              isTree: true,
              filterProtected: false,
              pickerPosition: "down",
              uiStyle: "extra",
              query: {
                "allow_matched": true
              }
              },
            {
              name: "handler",
              xtype: "main.handler.LookupField",
              fieldLabel: __("Match Handler"),
              allowBlank: true,
              uiStyle: "medium",
              query: {
                "allow_match_rule": true
              }
            }
            ]
        }
      ]
    });
    me.callParent();
  }
});
