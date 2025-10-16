//---------------------------------------------------------------------
// main.prefixtable application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.regexplabel.Application");

Ext.define("NOC.main.regexplabel.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.label.LabelField",
    "NOC.main.regexplabel.Model",
  ],
  model: "NOC.main.regexplabel.Model",
  search: true,
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
    },
    {
      name: "description",
      xtype: "textarea",
      fieldLabel: __("Description"),
      allowBlank: true,
    },
    {
      name: "regexp",
      xtype: "textfield",
      fieldLabel: __("REGEX"),
      allowBlank: false,
    },
    {
      name: "flag_multiline",
      xtype: "checkbox",
      boxLabel: __("Multiline"),
      allowBlank: true,
    },
    {
      name: "flag_dotall",
      xtype: "checkbox",
      boxLabel: __("DotALL"),
      allowBlank: true,
    },
    {
      name: "labels",
      xtype: "labelfield",
      fieldLabel: __("Labels"),
      allowBlank: true,
      query: {
        "enable_managedobject": true,
      },
    },
    {
      xtype: "fieldset",
      layout: "vbox",
      title: __("Enable"),
      defaults: {
        padding: 4,
        labelAlign: "right",
      },
      items: [
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("ManagedObject"),
          defaults: {
            padding: 4,
            labelAlign: "right",
          },
          items: [
            {
              name: "enable_managedobject_name",
              xtype: "checkbox",
              boxLabel: __("Managed Object Name"),
            },
            {
              name: "enable_managedobject_address",
              xtype: "checkbox",
              boxLabel: __("Managed Object Address"),
            },
            {
              name: "enable_managedobject_description",
              xtype: "checkbox",
              boxLabel: __("Managed Object Description"),
            },
          ],
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Interface"),
          defaults: {
            padding: 4,
            labelAlign: "right",
          },
          items: [
            {
              name: "enable_interface_name",
              xtype: "checkbox",
              boxLabel: __("Interface Name"),
            },
            {
              name: "enable_interface_description",
              xtype: "checkbox",
              boxLabel: __("Interface Description"),
            },
          ],
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Sensor"),
          defaults: {
            padding: 4,
            labelAlign: "right",
          },
          items: [
            {
              name: "enable_sensor_local_id",
              xtype: "checkbox",
              boxLabel: __("Sensor Local ID"),
            },
          ],
        },
      ]},
  ],
});
