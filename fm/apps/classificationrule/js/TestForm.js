//---------------------------------------------------------------------
// fm.classificationrule rule test form
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.classificationrule.TestForm");

Ext.define("NOC.fm.classificationrule.TestForm", {
    extend: "Ext.panel.Panel",
    app: null,

    initComponent: function() {
        var me = this;

        me.dataField = Ext.create("Ext.form.field.TextArea", {
            name: "data",
            labelAlign: "top",
            fieldLabel: "Event id or JSON code",
            width: 400,
            height: 200
        });

        Ext.apply(me, {
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: "Close",
                            glyph: NOC.glyph.arrow_left,
                            scope: me,
                            handler: me.onClose
                        },
                        {
                            text: "Test",
                            glyph: NOC.glyph.question_sign,
                            scope: me,
                            handler: me.onTest
                        }
                    ]
                }
            ],
            items: [
                me.dataField
            ]
        });
        me.callParent();
    },
    //
    onClose: function() {
        var me = this;
        me.app.showForm();
    },
    //
    onTest: function() {
        var me = this,
            data = me.dataField.getValue(),
            fd = me.app.getFormData();
        // @todo: Validation
        Ext.Ajax.request({
            url: "/fm/classificationrule/test/",
            method: "post",
            scope: me,
            jsonData: {
                data: data,
                patterns: me.app.getPatterns(),
                event_class: fd["event_class"]
            },
            success: function(response) {
                var me = this;
                me.onSuccess(Ext.decode(response.responseText));
            },
            failure: function() {
                NOC.error("Failed to test rule")
            }
        });
    },
    //
    onSuccess: function(data) {
        var me = this,
            item = me.app.showItem(me.app.ITEM_TEST_RESULT);
        item.preview({data: data});
    }
});
