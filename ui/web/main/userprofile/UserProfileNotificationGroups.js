//---------------------------------------------------------------------
// main.userprofile notification groups grid
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.userprofile.UserProfileNotificationGroups");

Ext.define("NOC.main.userprofile.UserProfileNotificationGroups", {
  extend: "Ext.grid.Panel",
  alias: "widget.userprofilenotification",
  requires: [
    "NOC.main.ref.unotificationmethod.LookupField",
    "NOC.main.timepattern.LookupField",
  ],
  selModel: "rowmodel",
  forceFit: true,
  plugins: {
    ptype: "rowediting",
    clicksToEdit: 1,
    listeners: {
      edit: function(editor, context){
        var record = context.record,
          store = context.store;
        Ext.Ajax.request({
          url: "/main/notificationgroup/" + record.get("notification_group") + "/change_user_subscription/",
          method: "POST",
          jsonData: {
            user_policy: record.get("user_policy"),
            time_pattern: record.get("time_pattern") || null,
            expired_at: record.get("expired_at"),
            title_tag: record.get("title_tag") || null,
            preferred_method: record.get("preferred_method") || null,
          },
          success: function(response){
            var result = Ext.decode(response.responseText);
            if(result.success){
              var data = store.getData().items;
              record.commit();
              // store.load({
              // callback: function(){
              NOC.info(__("Changes saved successfully"));
              // },
            // });
            } else{
              NOC.error(result.message || __("Failed to save changes"));
            }
          },
          failure: function(response){
            var text = Ext.decode(response.responseText); 
            NOC.error(text.message || __("Failed to save changes"));
          },
        });
      },
    },
  },
  store: {
    fields: [
      {name: "notification_group", type: "string"},
      {name: "user_policy", type: "string"},
      {name: "preferred_method", type: "string"},
      {name: "time_pattern", type: "number"},
      {name: "expired_at", type: "date"},
      {name: "title_tag", type: "string"},
      {name: "tag", type: "auto"},
    ],
    data: [],
  },
  columns: [
    {
      text: __("Notification Group"),
      dataIndex: "notification_group",
      renderer: NOC.render.Lookup("notification_group"),
    },
    {
      text: __("Policy"),
      dataIndex: "user_policy",
      editor: {
        xtype: "combobox",
        store: {
          fields: ["id", "name"],
          data: [
            {id: "A", name: __("All")},
            {id: "W", name: __("Only Watch")},
            {id: "F", name: __("Only Favorites")},
            {id: "D", name: __("Disable")},
          ],
        },
        displayField: "name",
        valueField: "id",
        queryMode: "local",
        editable: false,
      },
      renderer: function(v){
        var m = {
          A: __("All"),
          W: __("Only Watch"),
          F: __("Only Favorites"),
          D: __("Disable"),
        };
        return m[v];
      },
    },
    {
      text: __("Preferred Method"),
      dataIndex: "preferred_method",
      editor: "main.ref.unotificationmethod.LookupField",
      renderer: NOC.render.Lookup("preferred_method"),
    },
    {
      text: __("Time Pattern"),
      dataIndex: "time_pattern",
      editor: "main.timepattern.LookupField",
      renderer: NOC.render.Lookup("time_pattern"),
    },
    {
      text: __("title-tag"),
      dataIndex: "title_tag",
      editor: "textfield",
    },
    {
      text: __("Expired At"),
      dataIndex: "expired_at",
      editor: {
        xtype: "datefield",
        startDay: 1,
        format: "Y-m-d H:i:s",
        submitFormat: "Y-m-d H:i:s",
      },
      renderer: function(value){
        if(!value){
          return "";
        }
        return Ext.Date.format(new Date(value), "Y-m-d H:i:s");
      },
    },
    {
      text: __("Message Types"),
      dataIndex: "tag",
      renderer: function(v){
        if(Ext.isEmpty(v)){
          return "-";
        }
        if(Ext.isArray(v) && v.length > 0){
          return v.join(", ");
        }
        return v;
      },
    },
  ],
});