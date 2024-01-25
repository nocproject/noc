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
    "NOC.inv.cpeprofile.Model",
    "NOC.main.pool.LookupField",
    "NOC.main.ref.stencil.LookupField",
    "NOC.sa.managedobject.LookupField",
    "NOC.sa.managedobjectprofile.LookupField",
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
              "allow_models": ["inv.CPEProfile"]
          }
        },
        {
          name: "workflow",
          xtype: "wf.workflow.LookupField",
          fieldLabel: __("WorkFlow"),
          allowBlank: true
        },
        {
            xtype: "fieldset",
            title: __("Display Settings"),
            items: [
                {
                    name: "style",
                    xtype: "main.style.LookupField",
                    fieldLabel: __("Style"),
                    allowBlank: true
                },
                {
                    name: "shape",
                    xtype: "main.ref.stencil.LookupField",
                    fieldLabel: __("Shape"),
                    allowBlank: true
                },
                {
                    name: "shape_title_template",
                    xtype: "textarea",
                    maxLength: 250,
                    fieldLabel: __("Shape Name template"),
                    allowBlank: true,
                    width: 650,
                }
            ]
        },
        {
            xtype: "fieldset",
            title: __("ManagedObject Sync Settings"),
            items: [
                {
                    name: "sync_managedobject",
                    xtype: "checkbox",
                    boxLabel: __("Sync ManagedObject")
                },
                {
                    name: "object_profile",
                    xtype: "sa.managedobjectprofile.LookupField",
                    fieldLabel: __("Managed Object Profile"),
                    allowBlank: true
                },
                {
                    name: "pool",
                    xtype: "main.pool.LookupField",
                    fieldLabel: __("Pool"),
                    allowBlank: true
                }
            ]
        },
        {
          xtype: "fieldset",
          title: __("Asset Sync Settings"),
          items: [
              {
                  name: "sync_asset",
                  xtype: "checkbox",
                  boxLabel: __("Sync Asset")
              }
          ]
        },
        {
            name: "cpe_status_discovery",
            xtype: "combobox",
            fieldLabel: __("Status Discovery"),
            allowBlank: true,
            labelWidth: 200,
            defaultValue: "D",
            store: [
                ["D", __("Disabled")],
                ["E", __("Enable")]
            ],
            uiStyle: "medium"
        },
        {
            xtype: "container",
            layout: "hbox",
            defaults: {
                padding: "0 8 0 0"
            },
            items: [
                {
                    name: "metrics_default_interval",
                    xtype: "numberfield",
                    fieldLabel: __("Default Interval, sec"),
                    labelWidth: 200,
                    allowBlank: false,
                    uiStyle: "small",
                    minValue: 0,
                    listeners: {
                        scope: me,
                        change: function(_item, newValue, oldValue, eOpts) {
                            me.form.findField("metrics_default_interval_calculated").setValue(newValue);
                        }
                    }
                },
                {
                    name: 'metrics_default_interval_calculated',
                    xtype: 'displayfield',
                    renderer: NOC.render.Duration
                }
            ]
        },
        {
          name: "metrics_interval_buckets",
          xtype: "numberfield",
          fieldLabel: __("Metrics interval Buckets"),
          allowBlank: true,
          uiStyle: "medium",
          minValue: 0
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
                    }
                }
            ]
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
