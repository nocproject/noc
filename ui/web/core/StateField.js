//---------------------------------------------------------------------
// NOC.core.State
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.StateField");
Ext.define("NOC.core.StateField", {
    alias: "widget.statefield",
    extend: "Ext.form.FieldContainer",
    mixins: {
        field: "Ext.form.field.Field"
    },
    requires: [
        "NOC.core.StateModel"
    ],
    itemId: undefined,
    showTransitionCls: "fa fa-arrow-circle-right",
    shownTransitionCls: "fa fa-arrow-circle-down",

    initComponent: function () {
        var me = this;
        me.store = Ext.create("Ext.data.Store", {
            model: "NOC.core.StateModel",
            autoLoad: false,
            proxy: {
                type: "ajax",
                reader: "json"
            }
        });

        me.stateField = Ext.create("Ext.form.field.Text", {
            editable: false,
            triggers: {
                right: {
                    cls: me.showTransitionCls,
                    tooltip: __("Transition"),
                    hidden: false,
                    scope: me,
                    handler: me.showTransitions
                },
                down: {
                    cls: me.shownTransitionCls,
                    tooltip: __("Transition"),
                    hidden: true,
                    scope: me,
                    handler: me.hideTransitions
                }
            },
            uiStyle: "medium"
        });

        me.grid = Ext.create("Ext.grid.Panel", {
            hidden: true,
            border: false,
            bodyBorder: false,
            headerBorders: false,
            clearRemovedOnLoad: true,
            emptyText: __("No possible transitions"),
            store: me.store,
            componentCls: "arrow-up",
            columns: [
                {
                    xtype: "widgetcolumn",
                    width: 40,
                    widget: {
                        width: 25,
                        xtype: "button",
                        glyph: NOC.glyph.arrow_circle_right,
                        handler: function (btn) {
                            me.step(btn.getWidgetRecord())
                        }
                    }
                },
                {
                    text: __("Transition"),
                    flex: 1,
                    dataIndex: "label"
                },
                {
                    text: __("Description"),
                    flex: 3,
                    dataIndex: "description"
                }
            ],
            listeners: {
                rowdblclick: function (grid, rec) {
                    me.step(rec);
                }
            }
        });

        me.items = [
            me.stateField,
            me.grid
        ];

        me.callParent();
    },

    cleanValue: function (record, url) {
        var me = this;
        return {
            value: record.get(me.name),
            label: record.get(me.name + "__label"),
            itemId: record.get("id"),
            restUrl: url
        }
    },

    setValue: function (v) {
        var me = this;
        v = v || {};
        me.stateField.setValue(v.label || "");
        me.itemId = v.itemId || null;
        me.restUrl = v.restUrl || null;
    },

    step: function (rec) {
        var me = this;
        Ext.Msg.show({
            title: __("Transition"),
            msg: __("Do you wish to perform '" + rec.get("label") + "' transition? This operation cannot be undone!"),
            buttons: Ext.Msg.YESNO,
            icon: Ext.window.MessageBox.QUESTION,
            modal: true,
            fn: function (button) {
                if (button === "yes") {
                    me.doTransition(rec);
                }
            }
        });
    },

    doTransition: function (record) {
        var me = this,
            url = Ext.String.format("/crm/supplier/{0}/transitions/{1}/", me.itemId, record.get("id"));
        Ext.Ajax.request({
            url: url,
            method: "POST",
            success: function (response) {
                var data = Ext.decode(response.responseText);
                me.stateField.setValue(data.state__label);
                me.hideTransitions();
                NOC.msg.complete(__("Transition started"))
            },

            failure: function (response) {
                NOC.msg.failed(__("server-side failure with status code ") + response.status);
            }
        });
    },

    showTransitions: function () {
        var me = this;
        me.grid.show();
        me.stateField.getTriggers().right.hide();
        me.stateField.getTriggers().down.show();
        me.store.load({
            url: me.restUrl + me.itemId + "/transitions/"
        })
    },

    hideTransitions: function () {
        var me = this;
        me.stateField.getTriggers().right.show();
        me.stateField.getTriggers().down.hide();
        me.grid.hide()
    }
});