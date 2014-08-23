//---------------------------------------------------------------------
// NOC.core.RestTemplatePreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.RestTemplatePreview");

Ext.define("NOC.core.RestTemplatePreview", {
    extend: "NOC.core.TemplatePreview",

    initComponent: function() {
        var me = this;

        me.urlTemplate = Handlebars.compile(me.restUrl);
        me.callParent();
    },
    //
    preview: function(record, extra) {
        var me = this;

        if(!record) {
            me.items.first().update("No data!!!");
            return;
        }
        var url = me.urlTemplate(record.data);
        me.setTitle(me.titleTemplate(record.data));
        me.currentRecord = record;
        Ext.Ajax.request({
            url: url,
            method: "GET",
            scope: me,
            success: function(response) {
                var context = Ext.decode(response.responseText);
                me.setTitle(me.titleTemplate(record.data));
                me.items.first().update("<div class='noc-tp'>" + me.template(context) + "</div>");
            },
            failure: function() {
                NOC.error("Failed to get JSON")
            }
        });
    }
});
