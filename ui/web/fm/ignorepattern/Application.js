//---------------------------------------------------------------------
// fm.ignorepattern application
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.ignorepattern.Application");

Ext.define("NOC.fm.ignorepattern.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.fm.ignorepattern.Model",
  ],
  model: "NOC.fm.ignorepattern.Model",
  search: true,

  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      columns: [
        {
          text: __("Source"),
          dataIndex: "source",
          width: 75,
        },
        {
          text: __("Active"),
          dataIndex: "is_active",
          width: 25,
          renderer: NOC.render.Bool,
        },
        {
          text: __("Pattern"),
          dataIndex: "pattern",
          flex: 1,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
      ],
      fields: [
        {
          name: "source",
          xtype: "combobox",
          fieldLabel: __("Source"),
          allowBlank: false,
          store: [
            ["syslog", "SYSLOG"],
            ["SNMP Trap", "SNMP Trap"],
          ],
        },
        {
          name: "is_active",
          xtype: "checkbox",
          boxLabel: __("Active"),
        },
        {
          name: "pattern",
          xtype: "textfield",
          fieldLabel: __("Pattern (RE)"),
          allowBlank: false,
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
      ],
    });
    me.callParent();
  },
  onCmd_from_event: function(record){
    var body = {
      id: record.id,
      source: record.get("source"),
      target: record.get("target"),
      target_id: record.get("target_id"),
      managed_object_id: record.get("managed_object_id"),
      address: record.get("address"),
      event_class_id: record.get("event_class_id"),
      message: record.get("message"),
      snmp_trap_oid: record.get("snmp_trap_oid"),
      labels: record.get("labels"),
      raw_vars: record.get("raw_vars"),
      data: record.get("data"),
      remote_id: record.get("remote_id"),
      remote_system: record.get("remote_system"),
    };
    Ext.Ajax.request({
      url: "/fm/ignorepattern/from_event/" + record.id + "/",
      method: "POST",
      jsonData: body,
      scope: this,
      success: function(response){
        var data = Ext.decode(response.responseText);
        this.newRecord(data);
      },
      failure: function(){
        NOC.error(__("Failed to create ignore pattern from event"));
      },
    });
  },

});
