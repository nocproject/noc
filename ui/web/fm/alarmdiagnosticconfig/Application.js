//---------------------------------------------------------------------
// fm.alarmdiagnosticconfig application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmdiagnosticconfig.Application");

Ext.define("NOC.fm.alarmdiagnosticconfig.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.fm.alarmdiagnosticconfig.Model",
    "NOC.fm.alarmclass.LookupField",
    "NOC.main.ref.script.LookupField",
    "NOC.sa.action.LookupField",
    "NOC.core.combotree.ComboTree",
  ],
  model: "NOC.fm.alarmdiagnosticconfig.Model",
  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 100,
        },
        {
          text: __("Is Active"),
          dataIndex: "is_active",
          width: 50,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Alarm Class"),
          dataIndex: "alarm_class",
          flex: 1,
          renderer: NOC.render.Lookup("alarm_class"),
        },
      ],

      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
        },
        {
          xtype: "tabpanel",
          layout: "fit",
          autoScroll: true,
          anchor: "-0, -50",
          defaults: {
            autoScroll: true,
            layout: "anchor",
            padding: 10,
          },
          items: [
            {
              title: __("Common"),
              items: [
                {
                  name: "is_active",
                  xtype: "checkbox",
                  boxLabel: __("Active"),
                },
                {
                  name: "alarm_class",
                  xtype: "fm.alarmclass.LookupField",
                  fieldLabel: __("Alarm Class"),
                  uiStyle: "large",
                  allowBlank: false,
                },
                {
                  name: "only_root",
                  xtype: "checkbox",
                  boxLabel: __("Only Root"),
                },
                {
                  name: "resource_group",
                  xtype: "noc.core.combotree",
                  restUrl: "/inv/resourcegroup/",
                  fieldLabel: __("Resource Group"),
                  listWidth: 1,
                  listAlign: "left",
                  labelAlign: "left",
                  width: 500,
                },
                {
                  name: "description",
                  xtype: "textarea",
                  fieldLabel: __("Description"),
                  allowBlank: true,
                  anchor: "100%",
                },
              ],
            },
            {
              title: __("On Raise"),
              items: [
                {
                  name: "enable_on_raise",
                  xtype: "checkbox",
                  boxLabel: __("Enable"),
                },
                {
                  name: "on_raise_delay",
                  xtype: "numberfield",
                  fieldLabel: __("Delay"),
                  min: 0,
                  allowBlank: true,
                },
                {
                  name: "on_raise_header",
                  xtype: "textarea",
                  fieldLabel: __("Header"),
                  allowBlank: true,
                },
                {
                  name: "on_raise_script",
                  xtype: "main.ref.script.LookupField",
                  fieldLabel: __("Script"),
                  width: 150,
                  allowBlank: true,
                },
                {
                  name: "on_raise_action",
                  xtype: "sa.action.LookupField",
                  fieldLabel: __("Action"),
                  width: 150,
                  allowBlank: true,
                },
                {
                  name: "on_raise_handler",
                  xtype: "textfield",
                  fieldLabel: __("Handler"),
                  allowBlank: true,
                },
              ],
            },
            {
              title: __("Periodic"),
              items: [
                {
                  name: "enable_periodic",
                  xtype: "checkbox",
                  boxLabel: __("Enable"),
                },
                {
                  name: "periodic_interval",
                  xtype: "numberfield",
                  fieldLabel: __("Delay"),
                  min: 0,
                  allowBlank: true,
                },
                {
                  name: "periodic_header",
                  xtype: "textarea",
                  fieldLabel: __("Header"),
                  allowBlank: true,
                },
                {
                  name: "periodic_script",
                  xtype: "main.ref.script.LookupField",
                  fieldLabel: __("Script"),
                  width: 150,
                  allowBlank: true,
                },
                {
                  name: "periodic_action",
                  xtype: "sa.action.LookupField",
                  fieldLabel: __("Action"),
                  width: 150,
                  allowBlank: true,
                },
                {
                  name: "periodic_handler",
                  xtype: "textfield",
                  fieldLabel: __("Handler"),
                  allowBlank: true,
                },
              ],
            },
            {
              title: __("On Clear"),
              items: [
                {
                  name: "enable_on_clear",
                  xtype: "checkbox",
                  boxLabel: __("Enable"),
                },
                {
                  name: "on_clear_delay",
                  xtype: "numberfield",
                  fieldLabel: __("Delay"),
                  min: 0,
                  allowBlank: true,
                },
                {
                  name: "on_clear_header",
                  xtype: "textarea",
                  fieldLabel: __("Header"),
                  allowBlank: true,
                },
                {
                  name: "on_clear_script",
                  xtype: "main.ref.script.LookupField",
                  fieldLabel: __("Script"),
                  width: 150,
                  allowBlank: true,
                },
                {
                  name: "on_clear_action",
                  xtype: "sa.action.LookupField",
                  fieldLabel: __("Action"),
                  width: 150,
                  allowBlank: true,
                },
                {
                  name: "on_clear_handler",
                  xtype: "textfield",
                  fieldLabel: __("Handler"),
                  allowBlank: true,
                },
              ],
            },
          ],
        },
      ],
    });
    me.callParent();
  },
});
