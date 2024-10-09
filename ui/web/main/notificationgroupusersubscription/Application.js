//---------------------------------------------------------------------
// main.notificationgroupusersubscription application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.notificationgroupusersubscription.Application");

Ext.define("NOC.main.notificationgroupusersubscription.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.notificationgroupusersubscription.Model",
        "NOC.main.timepattern.LookupField",
        "NOC.main.template.LookupField",
        "NOC.main.remotesystem.LookupField",
        "NOC.aaa.user.LookupField"
    ],
    model: "NOC.main.notificationgroupusersubscription.Model",
    search: true,
    initComponent: function(){
      var me = this;

      Ext.apply(me, {
          columns: [
            {
              text: __("User"),
              dataIndex: "user",
              width: 350,
              renderer: NOC.render.Lookup("user")
            },
            {
              text: __("Expired At"),
              dataIndex: "expired_at",
              width: 150
            },
            {
                text: __("Supress"),
                dataIndex: "suppress",
                width: 50,
                renderer: NOC.render.Bool,
                sortable: false
            },
            {
              text: __("Notification Group"),
              dataIndex: "notification_group",
              width: 350,
              renderer: NOC.render.Lookup("notification_group")
            },
            {
              text: __("Time Pattern"),
              dataIndex: "time_pattern",
              width: 350,
              renderer: NOC.render.Lookup("time_pattern")
            },
            {
              text: __("Remote System"),
              dataIndex: "remote_system",
              width: 350,
              renderer: NOC.render.Lookup("remote_system")
            },
            {
              text: __("Watch"),
              dataIndex: "watch",
              width: 150
            }
          ],
          fields: [ ]
      });
      me.callParent();
    }
});
