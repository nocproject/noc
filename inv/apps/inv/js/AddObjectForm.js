//---------------------------------------------------------------------
// inv.inv AddObject form
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.AddObjectForm");

Ext.define("NOC.inv.inv.AddObjectForm", {
    extend: "Ext.panel.Panel",
    requires: ["NOC.inv.objectmodel.LookupField"],
    app: null,
    groupContainer: null,

    initComponent: function() {
        var me = this,
            title;

        if(me.groupContainer) {
            title = "Create new object in '" + me.groupContainer.get("name") + "'";
        } else {
            title = "Create new top-level object";
        }

        me.form = Ext.create("Ext.form.Panel", {
            bodyPadding: 4,
            layout: "anchor",
            defaults: {
                anchor: "100%",
                labelWidth: 40
            },
            items: [
                {
                    xtype: "inv.objectmodel.LookupField",
                    name: "type",
                    fieldLabel: "Type",
                    allowBlank: false
                },
                {
                    xtype: "textfield",
                    name: "name",
                    fieldLabel: "Name",
                    allowBlank: false
                }
            ]
        });

        Ext.apply(me, {
            title: title,
            items: [me.form],
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "top",
                    items: [
                        {
                            text: "Close",
                            scope: me,
                            glyph: NOC.glyph.arrow_left,
                            handler: me.onPressClose
                        },
                        {
                            text: "Add",
                            glyph: NOC.glyph.plus,
                            scope: me,
                            handler: me.onPressAdd
                        }
                    ]
                }
            ]
        });
        me.callParent();
    },

    setContainer: function(c) {
        var me = this;
        me.groupContainer = c;
    },

    onPressClose: function() {
        var me = this;
        me.app.showItem(me.app.ITEM_MAIN);
    },

    onPressAdd: function() {
        var me = this,
            values = me.form.getValues();
        Ext.Ajax.request({
            url: "/inv/inv/add_group/",
            method: "POST",
            jsonData: {
                name: values.name,
                type: values.type,
                container: me.groupContainer ? me.groupContainer.get("id") : null
            },
            scope: me,
            success: function() {
                me.app.showItem(me.app.ITEM_MAIN);
                if(me.groupContainer) {
                    me.app.store.reload({node: me.groupContainer});
                } else {
                    me.app.store.reload();
                }
            },
            failure: function() {
                NOC.error("Failed to save");
            }
        });
    }

});
