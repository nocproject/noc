//---------------------------------------------------------------------
// pm.metrictype application
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metrictype.Application");

Ext.define("NOC.pm.metrictype.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.CMText",
    "NOC.core.JSONPreviewII",
    "NOC.pm.metrictype.Model",
    "NOC.core.tagfield.Tagfield",
    "NOC.pm.metricscope.LookupField",
    "NOC.pm.measurementunits.LookupField",
    "NOC.pm.scale.LookupField",
  ],
  model: "NOC.pm.metrictype.Model",
  search: true,
  treeFilter: "category",
  initComponent: function(){
    var me = this;

    // JSON Panel
    me.jsonPanel = Ext.create("NOC.core.JSONPreviewII", {
      app: me,
      restUrl: "/pm/metrictype/{0}/json/",
      previewName: "Metric Type: {0}",
    });

    me.ITEM_JSON = me.registerItem(me.jsonPanel);

    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 150,
        },
        {
          text: __("Builtin"),
          dataIndex: "is_builtin",
          renderer: NOC.render.Bool,
          width: 50,
          sortable: false,
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
          regex: /^[a-zA-Z0-9\-\_ ]+( \| [a-zA-Z0-9\-\_ ]+)*$/,
        },
        {
          name: "uuid",
          xtype: "displayfield",
          fieldLabel: __("UUID"),
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          name: "scope",
          xtype: "pm.metricscope.LookupField",
          fieldLabel: __("Scope"),
          allowBlank: false,
        },
        {
          name: "field_name",
          xtype: "textfield",
          fieldLabel: __("Field Name"),
          allowBlank: false,
          regex: /[a-z][0-9a-z_]*/,
          uiStyle: "medium",
        },
        {
          name: "field_type",
          xtype: "combobox",
          fieldLabel: __("Field Type"),
          allowBlank: false,
          store: [
            ["UInt8", "UInt8"],
            ["Int8", "Int8"],
            ["UInt16", "UInt16"],
            ["Int16", "Int16"],
            ["UInt32", "UInt32"],
            ["Int32", "Int32"],
            ["UInt64", "UInt64"],
            ["Int64", "Int64"],
            ["Float32", "Float32"],
            ["Float64", "Float64"],
            ["String", "String"],
          ],
          uiStyle: "medium",
        },
        {
          xtype: "fieldset",
          title: __("Measurement Units"),
          tooltip: __("Set Measurements Unit for MetricType. Used for conversation value"),
          layout: "vbox",
          defaults: {
            labelAlign: "before",
            padding: 4,
          },
          items: [
            {
              xtype: "container",
              layout: "hbox",
              defaults: {
                padding: "0 8 0 0",
              },
              items: [
                {
                  name: "units",
                  xtype: "pm.measurementunits.LookupField",
                  fieldLabel: __("Metric Measurement Units"),
                  labelWidth: 150,
                  allowBlank: true,
                },
                {
                  name: "scale",
                  xtype: "pm.scale.LookupField",
                  fieldLabel: __("Metric Scale"),
                },
                {
                  name: "is_delta",
                  xtype: "checkbox",
                  boxLabel: __("Delta Value"),
                },
              ],
            },
          ],
          listeners: {
            render: me.addTooltip,
          },
        },
        {
          xtype: "fieldset",
          title: __("Compose Expression"),
          tooltip: __("Compose expression for MetricType. Worked only SAME Scope" +
                        "On expression use MetricType field_name as variable name"),
          layout: "vbox",
          defaults: {
            labelAlign: "top",
            padding: 4,
          },
          items: [
            {
              xtype: "container",
              layout: "hbox",
              defaults: {
                labelAlign: "top",
                padding: "0 8 0 0",
              },
              items: [
                {
                  xtype: "core.tagfield",
                  url: "/pm/metrictype/lookup/",
                  fieldLabel: __("Input Metric Type"),
                  tooltip: __("Metric Type inputs to Expression"),
                  name: "compose_inputs",
                  labelWidth: 150,
                  width: 300,
                  listeners: {
                    render: me.addTooltip,
                  },
                },
                {
                  name: "compose_expression",
                  xtype: "textarea",
                  fieldLabel: __("Compose Expression"),
                  allowBlank: true,
                  labelWidth: 150,
                  uiStyle: "medium",
                },
              ],
            },
          ],
          listeners: {
            render: me.addTooltip,
          },
        },
        {
          name: "agent_mappings",
          xtype: "gridfield",
          fieldLabel: __("Agent Mappings"),
          allowBlank: true,
          columns: [
            {
              text: __("Collector"),
              dataIndex: "collector",
              editor: "textfield",
              width: 100,
            },
            {
              text: __("Field"),
              dataIndex: "field",
              editor: "textfield",
              flex: 1,
            },
          ],
        },
      ],
      formToolbar: [
        {
          text: __("JSON"),
          glyph: NOC.glyph.file,
          tooltip: __("Show JSON"),
          hasAccess: NOC.hasPermission("read"),
          scope: me,
          handler: me.onJSON,
        },
      ],
    });
    me.callParent();
  },
  //
  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord, me.ITEM_FORM);
  },
});
