Ext.define("NOC.JIRA", {
    singleton: true,

    jira: "http://bt.nocproject.org/",
    //
    // Send inventory data. Returns issue id
    //
    sendInv: function(cfg) {
        var me = this,
            summary = cfg.summary || "",
            description = cfg.description || "",
            data = cfg.data,
            success = Ext.callback(cfg.success, me),
            failure = Ext.callback(cfg.failure, me);

        Ext.Ajax.request({
            url: me.jira + "rest/api/2/issue/",
            method: "POST",
            jsonData: {
                fields: {
                    project: {
                        key: "INV"
                    },
                    summary: summary,
                    description: description,
                    issuetype: {
                        name: "Improvement"
                    }
                }
            },
            //withCredentials: true,
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);
                success(data.key);
            },
            failure: function() {
                failure();
            }
        });
    }
});
