//---------------------------------------------------------------------
// ip.ipam.tools form controller
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.tools.ToolsController");

Ext.define("NOC.ip.ipam.view.forms.tools.ToolsController", {
    extend: "Ext.app.ViewController",
    alias: "controller.ip.ipam.form.tools",
    //
    onClose: function() {
        this.fireViewEvent("ipIPAMToolsFormClose");
    },
    //
    onDownload: function() {
        var prefix = this.getViewModel().get("prefix");

        Ext.Ajax.request({
            url: "/ip/tools/" + prefix.vrf + "/" + prefix.afi + "/" + prefix.name + "/download_ip/",
            method: "POST",
            success: function(response) {
                var blob = new Blob([response.responseText], {type: "text/plain;charset=utf-8"});
                NOC.saveAs(blob, "ips.csv");
            },
            failure: function(r) {
                var msg = r.responseText || r.statusText;
                NOC.error(msg);
            }
        });
    },
    //
    onStartZoneTransfer: function() {
        var model = this.getViewModel(),
            prefix = model.get("prefix"),
            data = {
                ns: model.get("ns"),
                zone: model.get("zone"),
            };
            Ext.apply(data);


        Ext.Ajax.request({
            url: "/ip/tools/" + prefix.vrf + "/" + prefix.afi + "/" + prefix.name + "/upload_axfr/",
            method: "POST",
            jsonData: data,
            success: function(r) {
                var msg = r.responseText || r.statusText;
                NOC.info(msg);
            },
            failure: function(r) {
                var msg = r.responseText || r.statusText;
                NOC.error(msg);
            }
        });
    }
});
