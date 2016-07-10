//---------------------------------------------------------------------
// MIB Upload Form
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.mib.MIBUpload");

Ext.define("NOC.fm.mib.MIBUpload", {
    extend: "Ext.Window",
    autoShow: true,
    modal: true,
    app: undefined,
    title: "Upload MIB",
    layout: "fit",

    initComponent: function() {
        var me = this;
        me.uploadFiles = [];
        for(var i = 0; i < 5; i++) {
            me.uploadFiles.push(
                Ext.create("Ext.form.field.File", {
                    name: "mib_" + i,
                    fieldLabel: "MIB #" + i,
                    labelWidth: 50,
                    width: 400,
                    buttonText: "Select MIB..."
                })
            );
        }
        me.form = Ext.create("Ext.form.Panel", {
            items: me.uploadFiles,
            dockedItems: [
                {
                    xtype: "toolbar",
                    dock: "bottom",
                    items: [
                        {
                            text: "Upload",
                            glyph: NOC.glyph.upload,
                            scope: me,
                            handler: me.onUpload
                        }
                    ]
                }
            ]
        });

        Ext.apply(me, {
            items: [
                me.form
            ]
        });
        me.callParent();
    },

    onUpload: function() {
        var me = this,
            form = me.form.getForm();
        if(form.isValid()) {
            form.submit({
                url: "/fm/mib/upload/",
                waitMsg: "Uploading MIBs...",
                success: function(form, action) {
                    NOC.info("MIBs has been uploaded");
                    me.close();
                },
                failure: function() {
                    NOC.error("Failed to upload MIB");
                }
            });
        }
    }
});
