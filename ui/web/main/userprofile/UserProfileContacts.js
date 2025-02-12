//---------------------------------------------------------------------
// main.userprofile contacts grid
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.userprofile.UserProfileContacts");

Ext.define("NOC.main.userprofile.UserProfileContacts", {
  extend: "Ext.ux.form.GridField",
  alias: "widget.userprofile.contacts",
  columns: [
    {
      text: __("Time Pattern"),
      dataIndex: "time_pattern",
      width: 150,
      renderer: NOC.render.Lookup("time_pattern"),
      editor: "main.timepattern.LookupField",
    },
    {
      text: __("Method"),
      dataIndex: "notification_method",
      width: 120,
      editor: "main.ref.unotificationmethod.LookupField",
    },
    {
      text: __("Params"),
      dataIndex: "params",
      flex: 1,
      editor: "textfield",
    },
  ],
  getValue: function(){
    var records = [];
    this.store.each(function(r){
      var d = {};
      Ext.each(this.fields, function(f){
        // ToDo change Ext.ux.form.GridField
        var field_name = f.name || f;
        d[field_name] = r.get(field_name);
      });
      records.push(d);
    });
    return records;
  },
});