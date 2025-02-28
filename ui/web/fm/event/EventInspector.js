//---------------------------------------------------------------------
// fm.event application inspector panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.event.EventInspector");

Ext.define("NOC.fm.event.EventInspector", {
  extend: "Ext.form.Panel",
  title: __("Event Inspector"),
  layout: "form",
  scrollable: true,
  bodyPadding: 4,

  items: [
    {
      xtype: "displayfield",
      fieldLabel: __("ID"),
      name: "id",
    },
    {
      xtype: "displayfield",
      fieldLabel: __("Managed Object"),
      name: "managed_object__label",
    },
  ],

  setRecord: function(record){
    if(!record){
      return;
    }
    this.getForm().setValues({
      id: record.get("id"),
      managed_object__label: record.get("managed_object__label"),
    });
  },
});