//---------------------------------------------------------------------
// MIB Upload Form
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.file.UploadForm");

Ext.define("NOC.inv.inv.plugins.file.UploadForm", {
    extend: "Ext.Window",
    autoShow: true,
    modal: true,
    app: undefined,
    title: "Upload Files",
    layout: "fit",
    app: null,

    initComponent: function() {
        var me = this;
        me.fields = [];
        for(var i = 0; i < 5; i++) {
            me.fields.push(
                Ext.create("Ext.form.field.File", {
                    name: "file_" + i,
                    fieldLabel: "File #" + i,
                    labelWidth: 90,
                    width: 500,
                    buttonText: "Select file..."
                })
            );
            me.fields.push({
                xtype: "textfield",
                name: "description_" + i,
                fieldLabel: "Description #" + i,
                labelWidth: 90,
                width: 500
            });
        }
        me.form = Ext.create("Ext.form.Panel", {
            items: me.fields,
            padding: 4,
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
                url: "/inv/inv/" + me.app.currentId + "/plugin/file/upload/",
                waitMsg: "Uploading files...",
                success: function(form, action) {
                    NOC.info("Files has been uploaded");
                    me.close();
                    me.app.refresh();
                },
                failure: function() {
                    NOC.error("Failed to upload files");
                }
            });
        }
    }
});
