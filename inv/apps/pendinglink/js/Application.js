//---------------------------------------------------------------------
// inv.pendinglink application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.pendinglink.Application");

Ext.define("NOC.inv.pendinglink.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.pendinglink.Model"
    ],
    model: "NOC.inv.pendinglink.Model",
    fields: [],

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: "expire",
                    dataIndex: "expire"
                },
                {
                    text: "local object",
                    dataIndex: "local_object"
                },
                {
                    text: "local_interface",
                    dataIndex: "local_interface"
                },
                {
                    text: "remote object",
                    dataIndex: "remote_object"
                },
                {
                    text: "remote interface",
                    dataIndex: "remote_interface"
                },
                {
                    text: "method",
                    dataIndex: "method"
                },
                {
                    text: "Approve Link",
                    xtype: "actioncolumn",
                    width: 150,
                    items: [{
                        icon: "/static/img/fam/silk/information.png",
                        tooltip: "Manually approve the link",
                        scope: me,
                        handler: me.onApprove
                    }]
                }
            ]
        });
        me.callParent();
    },
    //
    onApprove: function(grid, rowIndex, colIndex) {
        var me = this,
            link = me.store.getAt(rowIndex);
        me.approveLink(link);
    },
    //
    approveLink: function(link) {
        var me = this;
        Ext.Ajax.request({
            url: "/inv/pendinglink/" + link.get("id") + "/approve/",
            method: "POST",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                if(data.result) {
                    NOC.info(data.msg);
                } else {
                    NOC.error(data.msg);
                }
            },
            failure: function() {
                NOC.error("Failed to approve the link");
            }
        });
	}
});
