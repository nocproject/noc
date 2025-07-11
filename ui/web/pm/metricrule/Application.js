//---------------------------------------------------------------------
// pm.metricrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.metricrule.Application");

Ext.define("NOC.pm.metricrule.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.pm.metricrule.Model",
    "NOC.pm.metricaction.LookupField",
    "NOC.pm.metrictype.LookupField",
    "NOC.fm.alarmclass.LookupField",
    "NOC.core.label.LabelField",
    "NOC.core.ListFormField",
    "Ext.ux.form.GridField",
  ],
  model: "NOC.pm.metricrule.Model",
  search: true,

  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 100,
          align: "left",
        },
        {
          text: __("Active"),
          dataIndex: "is_active",
          renderer: NOC.render.Bool,
          width: 100,
          align: "left",
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "large",
        },
        {
          name: "is_active",
          xtype: "checkbox",
          boxLabel: __("Active"),
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          uiStyle: "large",
        },
        {
          name: "actions",
          xtype: "listform",
          fieldLabel: __("Actions"),
          rows: 8,
          // minHeight: 600,
          labelAlign: "top",
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
                  name: "is_active",
                  xtype: "checkbox",
                  isFormField: false,
                  boxLabel: __("Active"),
                  width: 100,
                },
                {
                  name: "metric_action",
                  xtype: "pm.metricaction.LookupField",
                  isFormField: false,
                  fieldLabel: __("Metric Action"),
                  listeners: {
                    scope: me,
                    select: me.onSelectQuery,
                  },
                  width: 400,
                  allowBlank: true,
                },
                {
                  xtype: "pm.metrictype.LookupField",
                  isFormField: false,
                  fieldLabel: __("Metric Type"),
                  tooltip: __("Metric Type inputs"),
                  name: "metric_type",
                  labelWidth: 150,
                  width: 500,
                  listeners: {
                    render: me.addTooltip,
                  },
                },
              ],
            },
            {
              name: "thresholds",
              xtype: "gridfield",
              isFormField: false,
              fieldLabel: __("Thresholds"),
              columns: [
                {
                  text: __("Op"),
                  dataIndex: "op",
                  width: 100,
                  editor: {
                    xtype: "combobox",
                    store: [
                      ["<", __("<")],
                      ["<=", __("<=")],
                      [">", __(">")],
                      [">=", __(">=")],
                    ],
                  },
                  renderer: NOC.render.Choices({
                    "<": __("<"),
                    "<=": __("<="),
                    ">": __(">"),
                    ">=": __(">="),
                  }),
                },
                {
                  text: __("Value"),
                  dataIndex: "value",
                  editor: {
                    xtype: "numberfield",
                    vtype: "float",
                    allowBlank: false,
                    emptyText: 2.0,
                    decimalPrecision: 2,
                  },
                },
                {
                  text: __("Clear Value"),
                  dataIndex: "clear_value",
                  editor: {
                    xtype: "numberfield",
                    vtype: "float",
                    allowBlank: true,
                  },
                },
                {
                  text: __("Alarm Class"),
                  dataIndex: "alarm_class",
                  width: 200,
                  editor: {
                    xtype: "fm.alarmclass.LookupField",
                  },
                  renderer: NOC.render.Lookup("alarm_class"),
                },
                {
                  text: __("Alarm Labels"),
                  dataIndex: "alarm_labels",
                  renderer: NOC.render.LabelField,
                  editor: {
                    xtype: "labelfield",
                    query: {
                      "enable_alarm": true,
                    },
                  },
                  width: 200,
                },
              ],
            },
            {
              name: "metric_action_params",
              xtype: "gridfield",
              isFormField: false,
              fieldLabel: __("Action Params"),
              columns: [
                {
                  dataIndex: "name",
                  text: __("Name"),
                  width: 150,
                },
                {
                  dataIndex: "type",
                  text: __("Type"),
                  width: 70,
                },
                {
                  dataIndex: "value",
                  text: __("Value"),
                  editor: "textfield",
                  width: 200,
                },
                {
                  dataIndex: "min_value",
                  text: __("Min.Value"),
                  width: 70,
                },
                {
                  dataIndex: "max_value",
                  text: __("Max.Value"),
                  width: 70,
                },
                {
                  dataIndex: "default",
                  text: __("Default"),
                  width: 100,
                },
                {
                  dataIndex: "description",
                  text: __("Description"),
                  flex: 1,
                },
              ],
            },
          ],
        },
        {
          name: "match",
          xtype: "listform",
          fieldLabel: __("Match Rules"),
          labelAlign: "top",
          rows: 5,
          items: [
            {
              name: "labels",
              xtype: "labelfield",
              isFormField: false,
              fieldLabel: __("Match Labels"),
              allowBlank: true,
              isTree: true,
              filterProtected: false,
              pickerPosition: "down",
              uiStyle: "extra",
              query: {
                "allow_matched": true,
              },
            },
            {
              name: "exclude_labels",
              xtype: "labelfield",
              isFormField: false,
              fieldLabel: __("Exclude Match Labels"),
              allowBlank: true,
              isTree: true,
              filterProtected: false,
              pickerPosition: "down",
              uiStyle: "extra",
              query: {
                "allow_matched": true,
              },
            },
          ],
        },
      ],
    });
    me.callParent();
  },
  //
  onSelectQuery: function(field, record){
    var me = this,
      form = field.up("[xtype=form]"),
      queryParamsField = form.down("gridfield[name=metric_action_params]");
    if(record && record.isModel){
      Ext.Ajax.request({
        url: "/pm/metricaction/" + record.get("id") + "/",
        scope: me,
        success: function(response){
          var data = Ext.decode(response.responseText);
          queryParamsField.setValue(data.params);
        },
      })
    } else{
      queryParamsField.store.removeAll();
    }
  },
});
