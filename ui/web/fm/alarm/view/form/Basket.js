//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.form.Basket");

Ext.define("NOC.fm.alarm.view.form.Basket", {
    extend: "Ext.form.Panel",
    alias: "widget.fm.alarm.basket",
    layout: "anchor",
    scrollable: "y",
    defaults: {
    },
    items: [
        {
            xtype: "container",
            html: "Basket",
            itemId: "formTitle",
            padding: 4,
            style: {
                fontWeight: "bold"
            }
        },
        {
            xtype: "form",
            itemId: "fmAlarmBasketForm",
            defaults: {
                margin: 20
            }
        },
        {
            xtype: "grid",
            itemId: "fmAlarmBasketGrid",
            height: 500,
            columns: [
                {text: "Managed Object", dataIndex: "label", flex: 1},
            ],
            autoLoad: true,
            store: {
                fields: ["id", "label"],
                pageSize: 50,
                proxy: {
                    type: "rest",
                    url: "/sa/managedobject/lookup/",
                    pageParam: "__page",
                    startParam: "__start",
                    limitParam: "__limit",
                    sortParam: "__sort",
                    extraParams: {
                        "__format": "ext"
                    },
                    reader: {
                        type: "json",
                        rootProperty: "data",
                        totalProperty: "total",
                        successProperty: "success"
                    }
                }
            }
        }
    ],
    tbar: [
        {
            xtype: "button",
            text: __("Close"),
            handler: function(button) {
                button.up("[reference=fmAlarmBasket]").fireEvent("fmAlarmBasketClose", button);
            }
        },
        {
            xtype: "button",
            text: __("Apply"),
            handler: function(button) {
                var form = button.up("[reference=fmAlarmBasket]").down("[itemId=fmAlarmBasketForm]")
                console.log(form);
            }
        },
        {
            xtype: "button",
            text: __("Save"),
            handler: function(button) {
                var form = button.up("[reference=fmAlarmBasket]").down("[itemId=fmAlarmBasketForm]");
            }
        }
    ]
});