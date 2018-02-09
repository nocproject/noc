//---------------------------------------------------------------------
// inv.inv Contacts panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.contacts.ContactsPanel");

Ext.define("NOC.inv.inv.plugins.contacts.ContactsPanel", {
    extend: "Ext.panel.Panel",
    requires: [
    ],
    title: __("Contacts"),
    closable: false,
    layout: "fit",
    autoScroll: true,

    initComponent: function() {
        var me = this;

        me.displayAdminField = Ext.create("Ext.container.Container", {
            padding: 4,
            autoScroll: true
        });

        me.editAdminField = Ext.create("Ext.form.field.HtmlEditor", {
            hidden: true
        });

        me.displayBillField = Ext.create("Ext.container.Container", {
            padding: 4,
            autoScroll: true
        });

        me.editBillField = Ext.create("Ext.form.field.HtmlEditor", {
            hidden: true
        });

        me.displayTechField = Ext.create("Ext.container.Container", {
            padding: 4,
            autoScroll: true
        });

        me.editTechField = Ext.create("Ext.form.field.HtmlEditor", {
            hidden: true
        });

        me.editButton = Ext.create("Ext.button.Button", {
            text: __("Edit"),
            glyph: NOC.glyph.edit,
            scope: me,
            handler: me.onEdit
        });

        me.saveButton = Ext.create("Ext.button.Button", {
            text: __("Save"),
            glyph: NOC.glyph.save,
            scope: me,
            handler: me.onSave,
            hidden: true
        });

        // Grids
        Ext.apply(me, {
            items: [
                {
                    xtype: "container",
                    html: "Administrative Contacts"
                },
                me.displayAdminField,
                me.editAdminField,
                {
                    xtype: "container",
                    html: "Billing Contacts"
                },
                me.displayBillField,
                me.editBillField,
                {
                    xtype: "container",
                    html: "Technical Contacts"
                },
                me.displayTechField,
                me.editTechField
            ],
            dockedItems: [{
                xtype: "toolbar",
                dock: "top",
                items: [
                    me.editButton,
                    me.saveButton
                ]
            }]
        });
        me.callParent();
    },
    //
    preview: function(data) {
        var me = this;
        me.currentId = data.id;
        me.displayAdminField.update(data.contacts_administrative);
        me.editAdminField.update(data.contacts_administrative);
        me.displayBillField.update(data.contacts_billing);
        me.editBillField.update(data.contacts_billing);
        me.displayTechField.update(data.contacts_technical);
        me.editTechField.update(data.contacts_technical);
    },
    //
    onEdit: function() {
        var me = this;
        // Toolbar
        me.editButton.hide();
        me.saveButton.show();
        // Swap buttons
        me.displayAdminField.hide();
        me.editAdminField.show();
        me.displayBillField.hide();
        me.editBillField.show();
        me.displayTechField.hide();
        me.editTechField.show();
    },
    //
    onSave: function() {
        var me = this,
            adminValue = me.editAdminField.getValue(),
            billValue = me.editBillField.getValue(),
            techValue = me.editTechField.getValue();
        Ext.Ajax.request({
            url: "/inv/inv/" + me.currentId + "/plugin/contacts/",
            method: "POST",
            jsonData: {
                administrative: adminValue,
                billing: billValue,
                technical: techValue
            },
            scope: me,
            success: function() {
                me.editButton.show();
                me.saveButton.hide();
                me.editAdminField.hide();
                me.editBillField.hide();
                me.editTechField.hide();
                me.displayAdminField.update(adminValue);
                me.displayBillField.update(billValue);
                me.displayTechField.update(techValue);
                me.displayAdminField.show();
                me.displayBillField.show();
                me.displayTechField.show();
            },
            failure: function() {
                NOC.error(__("Failed to save data"));
            }
        });
    }
});
