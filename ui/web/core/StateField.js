//---------------------------------------------------------------------
// NOC.core.State
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
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
    currentRecord: undefined,
    inEditor: true,  // Do not inject result into .getFormData()

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
            cls: "noc-wc-state",
            baseBodyCls: "noc-wc-state-base-body",
            uiStyle: "medium",
            editable: false,
            inEditor: true,  // Do not inject result into .getFormData()
            triggers: {
                right: {
                    cls: me.showTransitionCls,
                    hidden: false,
                    scope: me,
                    handler: me.showTransitions
                },
                down: {
                    cls: me.shownTransitionCls,
                    hidden: true,
                    scope: me,
                    handler: me.hideTransitions
                }
            },
            listeners: {
                afterrender: function (field) {
                    Ext.tip.QuickTipManager.register({
                        target: field.getId(),
                        text: __("Transition")
                    });
                }
            }
        });

        me.gridContainer = Ext.create("Ext.container.Container", {
            cls: "noc-wc-cloud",
            hidden: true,
            width: 500,
            items: [
                {
                    xtype: "grid",
                    padding: 5,
                    border: false,
                    bodyBorder: false,
                    headerBorders: false,
                    hideHeaders: true,
                    clearRemovedOnLoad: true,
                    emptyText: __("No possible transitions"),
                    store: me.store,
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
                }
            ]
        });

        me.items = [
            me.stateField,
            me.gridContainer
        ];

        me.callParent();
    },

    cleanValue: function (record, url) {
        var me = this;
        me.currentRecord = record;
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
        me.hideTransitions();
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
            url = Ext.String.format("{0}{1}/transitions/{2}/", me.restUrl, me.itemId, record.get("id"));
        Ext.Ajax.request({
            url: url,
            method: "POST",
            success: function (response) {
                var data = Ext.decode(response.responseText);
                me.setValue({
                    value: data.state,
                    label: data.state__label,
                    itemId: me.itemId,
                    restUrl: me.restUrl
                });
                if(me.currentRecord) {
                    me.currentRecord.set(me.name, data.state);
                    me.currentRecord.set(me.name + "__label", data.state__label)
                }
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
        me.gridContainer.show();
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
        me.gridContainer.hide()
    }
});