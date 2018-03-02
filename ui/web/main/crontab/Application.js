//---------------------------------------------------------------------
// main.crontab application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.crontab.Application");

Ext.define("NOC.main.crontab.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.main.crontab.Model"
    ],
    model: "NOC.main.crontab.Model",
    search: true,

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 150
                },
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    width: 25,
                    renderer: NOC.render.Bool
                },
                {
                    text: __("CronTab"),
                    dataIndex: "crontab_expression",
                    width: 200
                },
                {
                    text: __("Handler"),
                    dataIndex: "handler",
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: __("Active")
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                    name: "handler",
                    xtype: "textfield",
                    fieldLabel: __("Handler"),
                    allowBlank: false,
                    uiStyle: "medium"
                    // vtype: "handler"
                },
                {
                    name: "seconds_expr",
                    xtype: "textfield",
                    fieldLabel: __("Seconds Expr."),
                    allowBlank: true,
                    uiStyle: "medium",
                    emptyText: "0"
                },
                {
                    name: "minutes_expr",
                    xtype: "textfield",
                    fieldLabel: __("Minutes Expr."),
                    allowBlank: true,
                    uiStyle: "medium",
                    emptyText: "*"
                },
                {
                    name: "hours_expr",
                    xtype: "textfield",
                    fieldLabel: __("Hours Expr."),
                    allowBlank: true,
                    uiStyle: "medium",
                    emptyText: "*"
                },
                {
                    name: "days_expr",
                    xtype: "textfield",
                    fieldLabel: __("Days Expr."),
                    allowBlank: true,
                    uiStyle: "medium",
                    emptyText: "*"
                },
                {
                    name: "months_expr",
                    xtype: "textfield",
                    fieldLabel: __("Months Expr."),
                    allowBlank: true,
                    uiStyle: "medium",
                    emptyText: "*"
                },
                {
                    name: "weekdays_expr",
                    xtype: "textfield",
                    fieldLabel: __("Weekdays Expr."),
                    allowBlank: true,
                    uiStyle: "medium",
                    emptyText: "*"
                },
                {
                    name: "years_expr",
                    xtype: "textfield",
                    fieldLabel: __("Years Expr."),
                    allowBlank: true,
                    uiStyle: "medium",
                    emptyText: "*"
                }
            ]
        });
        me.callParent();
    },
    filters: [
        {
            title: __("By Active"),
            name: "is_active",
            ftype: "boolean"
        }
    ]
});
