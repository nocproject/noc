// fm.reportalarmcomments application
//---------------------------------------------------------------------
// Copyright (C) 2007-2020 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.reportalarmcomments.Application");

Ext.define("NOC.fm.reportalarmcomments.Application", {
  extend: "NOC.core.Application",
  requires: [
    "NOC.core.ReportControl",
    "NOC.sa.administrativedomain.TreeCombo",
    "NOC.core.tagfield.Tagfield",
  ],

  items: {
    xtype: "report.control",
    url: "/fm/reportalarmcomments",
    controls: [
      // {
      //     name: "source",
      //     xtype: "segmentedbutton",
      //     allowBlank: false,
      //     width: 300,
      //     items: [
      //         {text: __("Active Alarms"), value: 'active', pressed: true},
      //         {text: __("Archived Alarms"), value: 'archive'},
      //         {text: __("Both"), value: 'both'}
      //     ]
      // },
      {
        name: "source",
        xtype: "radiogroup",
        columns: 4,
        vertical: false,
        fieldLabel: __("Alarms source"),
        allowBlank: false,
        width: 600,
        items: [
          {boxLabel: __("Both"), inputValue: "both", checked: true}],
        // {boxLabel: __("Long Alarm Archive (more 3 months)"), inputValue: 'long_archive'}]
      },
      {
        name: "from_date",
        xtype: "datefield",
        startDay: 1,
        fieldLabel: __("From"),
        allowBlank: false,
        format: "d.m.Y",
        submitFormat: "d.m.Y",
      },
      {
        name: "to_date",
        xtype: "datefield",
        startDay: 1,
        fieldLabel: __("To"),
        allowBlank: false,
        format: "d.m.Y",
        submitFormat: "d.m.Y",
      },
      {
        name: "administrative_domain",
        xtype: "sa.administrativedomain.TreeCombo",
        fieldLabel: __("By Adm. domain"),
        listWidth: 1,
        listAlign: "left",
        labelAlign: "left",
        width: 500,
        allowBlank: true,
      },
      {
        name: "enable_autowidth",
        xtype: "checkboxfield",
        boxLabel: __("Enable Excel column autowidth"),
        allowBlank: false,
      },
    ],
    storeData: [
      ["alarm_class", __("Alarm Class"), true],
      ["id", __("ID"), false],
      ["alarm_from_ts", __("From"), true],
      ["alarm_to_ts", __("To"), true],
      ["alarm_tt", __("Alarm TT"), true],
      ["object_name", __("Object Name"), true],
      ["object_address", __("IP"), true],
      ["object_admdomain", __("Administrative Domain"), true],
      ["log_timestamp", __("Comment Time"), true],
      ["log_source", __("Comment Source"), true],
      ["log_message", __("Comment Message"), true],
      // ["escalation_ts", __("Escalation Time"), true],
    ],
  },
});
