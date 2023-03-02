//---------------------------------------------------------------------
// main.desktop.report application
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug('Defining NOC.main.desktop.Report');

Ext.define('NOC.main.desktop.Report', {
    extend: 'NOC.core.Application',
    requires: [
        "NOC.core.ComboBox",
        "NOC.core.ReportControl",
        "NOC.core.combotree.ComboTree",
        "NOC.main.desktop.ReportColSelect",
    ],
    items: [],
    initComponent: function() {
        var me = this;

        me.formTitle = Ext.create("Ext.container.Container", {
            html: __("Report"),
            style: {
                padding: "10",
                fontSize: "1.2em",
                fontWeight: "bold",
            }
        });

        me.form = Ext.create("Ext.form.Panel", {
            layout: "anchor",
            scrollable: "vertical",
            defaults: {
                anchor: "70%",
                style: {
                    padding: "0 10",
                },
            },
            items: [
                me.formTitle,
            ]
        });

        Ext.apply(me, {
            items: [
                me.form,
                me.result
            ]
        });
        Ext.Ajax.request({
            url: "/main/reportconfig/" + me.noc.report_id + "/form/",
            method: "GET",
            scope: me,
            success: function(response) {
                var data = Ext.decode(response.responseText);

                this.form.addDocked({
                    xtype: 'toolbar',
                    dock: 'top',
                    items: Ext.Array.map(data.dockedItems, function(button) {
                        return Ext.apply(button, {
                            formBind: true,
                            handler: Ext.pass(this.submitForm, button, this),
                        });
                    }, this),
                });
                this.formTitle.setHtml(data.title);
                Ext.Array.each(data.params, function(field) {
                    this.form.add(field);
                }, this);
            },
            failure: function() {
                NOC.error(__("Failed to get params form"));
            }
        });
        me.callParent();
    },
    submitForm: function(button) {
        var params = Ext.Object.toQueryString(Ext.apply({output_type: button.param.output_type}, this.form.getValues())),
            url = "/main/reportconfig/" + this.noc.report_id + "/run?" + params;

        this.form.remove(this.down("[itemId=reportResult]"));
        Ext.Ajax.request({
            url: url,
            method: "GET",
            scope: this,
            success: function(response) {
                if(button.param.output_type === "html") {
                    // var htmlWrapperStart = '<head><link rel = "stylesheet" type = "text/css" href = "/ui/pkg/django-media/admin/css/base.css"/><link rel="stylesheet" type="text/css" href="/ui/web/css/django/main.css"/><link rel="stylesheet" type="text/css" href="/ui/pkg/fontawesome/css/font-awesome.min.css"/>    <link rel="stylesheet" type="text/css" href="/ui/web/css/colors.css"/></head><body><div id="container"><div id="content" class="colM">',
                    // htmlWrapperEnd = '</div></body></html >';
                    this.form.add({
                        itemId: "reportResult",
                        border: false,
                        html: response.responseText,
                        anchor: "100%",
                    });
                } else {
                    window.open(url);
                }
            },
            failure: function() {
                NOC.error(__("Failed to run report"));
            }
        });
    },
});
