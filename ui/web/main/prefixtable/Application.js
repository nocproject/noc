//---------------------------------------------------------------------
// main.prefixtable application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.prefixtable.Application");

Ext.define("NOC.main.prefixtable.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.main.prefixtable.Model",
    "Ext.ux.form.GridField",
    "NOC.core.label.LabelField",
  ],
  model: "NOC.main.prefixtable.Model",
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
      name: "match_labels",
      xtype: "gridfield",
      fieldLabel: __("Match Labels"),
      disabled: true,
      columns: [
        {
          text: __("Labels"),
          dataIndex: "labels",
          renderer: NOC.render.LabelField,
          editor: {
            xtype: "labelfield",
          },
          width: 200,
        },
        {
          dataIndex: "scope",
          text: __("Scope"),
          editor: "textfield",
          width: 150,
        },
      ],
    },
  ],
  inlines: [{
    title: __("Prefixes"),
    model: "NOC.main.prefixtable.PrefixModel",
    columns: [
      {
        text: __("Prefix"),
        dataIndex: "prefix",
        flex: 1,
        editor: "textfield",
      },
    ],
  }],
  actions: [
    {
      title: __("Test selected prefix tables ..."),
      action: "test",
      resultTemplate: new Ext.XTemplate('<b>IP:</b> {ip}\n<table border="1">\n    <tr><th>Prefix Table</th><th>Result</th></tr>\n    <tpl foreach="result">\n    <tr><td>{name}</td><td><tpl if="result">+<tpl else>-</tpl></td></tr>\n    </tpl>\n</table>'),
      form: [
        {
          name: "ip",
          xtype: "textfield",
          fieldLabel: __("IP"),
          allowBlank: false,
        },
      ],
    },
  ],
});
