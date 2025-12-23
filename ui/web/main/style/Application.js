//---------------------------------------------------------------------
// main.style application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.style.Application");

Ext.define("NOC.main.style.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.style.Model",
    "Ext.ux.form.ColorField",
  ],
  model: "NOC.main.style.Model",
  rowClassField: "row_class",
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
    },
    {
      text: __("Active"),
      dataIndex: "is_active",
      renderer: NOC.render.Bool,
      width: 50,
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
      name: "is_active",
      xtype: "checkboxfield",
      boxLabel: __("Is Active"),
      allowBlank: false,
    },
    {
      name: "description",
      xtype: "textarea",
      fieldLabel: __("Description"),
      allowBlank: true,
    },
    {
      xtype: "fieldset",
      title: __("Colors"),
      layout: "hbox",
      defaults: {
        xtype: "colorfield",
        labelAlign: "top",
        margin: "0 8 0 0",
        width: 135,
        allowBlank: false,
      },
      items: [
        {
          name: "font_color",
          fieldLabel: __("Font"),
        },
        {
          name: "background_color",
          fieldLabel: __("Background"),
        },
      ]},
    {
      xtype: "fieldset",
      title: __("Style"),
      layout: "hbox",
      defaults: {
        margin: "0 8 0 0",
        allowBlank: false,
      },
      items: [
        {
          name: "bold",
          xtype: "checkboxfield",
          boxLabel: __("Bold"),
        },
        {
          name: "italic",
          xtype: "checkboxfield",
          boxLabel: __("Italic"),
        },
        {
          name: "underlined",
          xtype: "checkboxfield",
          boxLabel: __("Underlined"),
        },
      ]},
  ],
  filters: [
    {
      title: __("By Active"),
      name: "is_active",
      ftype: "boolean",
    },
  ],
  onSave: function(){
    var data = this.form.getValues(),
      root = document.documentElement,
      id = this.currentRecord.id;
    this.callParent(arguments);
    root.style.setProperty(`--noc-color-${id}`, data.font_color);
    root.style.setProperty(`--noc-color-${id}-bg`, data.background_color);
    root.style.setProperty(`--noc-color-${id}-fw`, data.bold ? "bold" : "normal");
    root.style.setProperty(`--noc-color-${id}-fs`, data.italic ? "italic" : "normal");
    root.style.setProperty(`--noc-color-${id}-td`, data.underlined ? "underline" : "none");
  },
});
