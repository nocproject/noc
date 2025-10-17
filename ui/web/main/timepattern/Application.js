//---------------------------------------------------------------------
// main.timepattern application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.timepattern.Application");

Ext.define("NOC.main.timepattern.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.timepattern.Model",
    "NOC.main.timepattern.TermModel",
  ],
  model: "NOC.main.timepattern.Model",
  search: true,
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
      width: 100,
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
  ],
  inlines: [
    {
      title: __("Time Patterns"),
      model: "NOC.main.timepattern.TermModel",
      columns: [
        {
          text: __("Pattern"),
          dataIndex: "term",
          flex: 1,
          editor: "textfield",
        },
      ],
    },
  ],
  "actions": [
    {
      title: __("Test selected patterns"),
      action: "test",
      resultTemplate: new Ext.XTemplate('<b>Date:</b> {ts}\n<table border="1">\n    <tr><th>TimePattern</th><th>Result</th></tr>\n    <tpl foreach="result">\n    <tr><td>{name}</td><td><tpl if="result">+<tpl else>-</tpl></td></tr>\n    </tpl>\n</table>'),
      form: [
        {
          name: "date",
          xtype: "datefield",
          startDay: 1,
          fieldLabel: __("Date"),
          allowBlank: false,
          format: "Y-m-d",
        },
        {
          name: "time",
          xtype: "timefield",
          fieldLabel: __("Time"),
          allowBlank: true,
          format: "H:i",
        },
      ],
    },
  ],
});
