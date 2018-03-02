//---------------------------------------------------------------------
// Form Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.FormPanel");

Ext.define("NOC.core.FormPanel", {
    extend: "Ext.Container",
    layout: "fit",
    app: undefined,
    fields: [],
    restUrl: null,
    enableSaveButton: true,
    enableCloseButton: true,
    enableDeleteButton: false,
    formToolbar: null,
    title: "Title",

    initComponent: function() {
        var me = this;

        me.formTitle = Ext.create("Ext.container.Container", {
            minWidth: me.formMinWidth,
            maxWidth: me.formMaxWidth,
            html: me.title,
            itemId: "form_title",
            padding: "0 0 4 0",
            style: {
                fontSize: "1.2em",
                fontWeight: "bold"
            }
        });
        // Build form fields
        var formFields = [me.formTitle];
        // Append configured fields
        formFields = formFields.concat(me.getFormFields());

        Ext.apply(me, {
            items: [{
                xtype: 'form',
                layout: 'anchor',
                border: true,
                padding: 4,
                bodyPadding: 4,
                autoScroll: true,
                defaults: {
                    anchor: "100%",
                    enableKeyEvents: true,
                    listeners: {
                        specialkey: {
                            scope: me,
                            fn: me.onFormSpecialKey
                        }
                    }
                },
                items: formFields,
                dockedItems: {
                    xtype: "toolbar",
                    dock: "top",
                    layout: {
                        overflowHandler: "Menu"
                    },
                    items: me.getFormToolbar()
                }
            }]
        });
        me.callParent();
        me.form = me.items.first().getForm()
    },
    //
    preview: function(record, backItem) {
        var me = this;
    },
    // Form hotkeys processing
    onFormSpecialKey: function(field, key) {
        var me = this;
        if(field.xtype !== "textfield")
            return;
        switch(key.getKey()) {
            case Ext.EventObject.ENTER:
                key.stopEvent();
                //me.onSave();
                break;
            case Ext.EventObject.ESC:
                key.stopEvent();
                //me.onReset();
                break;
        }
    },
    //
    getFormFields: function() {
        var me = this;
        return me.fields
    },
    //
    getField: function(name) {
        var me = this,
            fields = me.form.getFields().items;
        for(var i = 0; i < fields.length; i++) {
            if(fields[i].getName && fields[i].getName() === name) {
                return fields[i]
            }
        }
        return undefined
    },
    //
    getFormToolbar: function() {
        var me = this,
            items = [];
        // //
        // me.resetButton = Ext.create("Ext.button.Button", {
        //     itemId: "reset",
        //     text: __("Reset"),
        //     tooltip: __("Reset to default values"),
        //     glyph: NOC.glyph.undo,
        //     disabled: true,
        //     scope: me,
        //     handler: me.onReset
        // });
        //
        if(me.enableSaveButton) {
            items.push(
                Ext.create("Ext.button.Button", {
                    itemId: "save",
                    text: __("Save"),
                    tooltip: __("Save changes"),
                    glyph: NOC.glyph.save,
                    formBind: true,
                    disabled: true,
                    scope: me,
                    // @todo: check access
                    handler: me.onSave
                })
            )
        }

        if(me.enableCloseButton) {
            items.push(
                Ext.create("Ext.button.Button", {
                    itemId: "close",
                    text: __("Close"),
                    tooltip: __("Close without saving"),
                    glyph: NOC.glyph.arrow_left,
                    scope: me,
                    handler: me.onClose
                })
            )
        }
        //
        if(me.enableDeleteButton) {
            if(items.length > 0) {
                items.push("-")
            }
            me.deleteButton = Ext.create("Ext.button.Button", {
                itemId: "delete",
                text: __("Delete"),
                tooltip: __("Delete object"),
                glyph: NOC.glyph.times,
                disabled: true,
                hasAccess: NOC.hasPermission("delete"),
                scope: me,
                handler: me.onDelete
            });
            items.push(me.deleteButton);
            items.push("-")
        }
        if(me.formToolbar) {
            var seen = me.app.applyPermissions(me.formToolbar);
            if(seen.length > 0) {
                items.push("-");
                items = items.concat(seen);
            }
        }
        return items
    },
    //
    onClose: Ext.emptyFn,
    //
    save: function(data) {

    },
    //
    onSave: function() {
        var me = this;
        if(!me.form.isValid()) {
            NOC.error(__("Error in data"));
            return
        }
        var v = me.getFormData();
        //
        me.cleanData(v);
        // Fetch comboboxes labels
        // me.form.getFields().each(function(field) {
        //     if(Ext.isDefined(field.getLookupData)) {
        //         v[field.name + "__label"] = field.getLookupData();
        //     }
        // });
        //
        me.save(v)
    },
    //
    onReset: function() {
        var me = this;
        me.form.reset()
    },
    //
    setValues: function(data) {
        var me = this,
            r = {},
            field;
        // Monkeypatch data to mimic Ext.data.Model
        data.get = function(key) {
            return data[key]
        };
        // Clean values
        Ext.iterate(data, function(v) {
            // Skip lookup values
            if(v.indexOf("__") !== -1) {
                return
            }
            // @todo: .TreeCombo
            field = me.form.findField(v);
            if(!field) {
                return;  // Value for unknown field
            }
            if(Ext.isFunction(field.cleanValue)) {
                r[v] = field.cleanValue(
                    data,
                    me.restUrl
                )
            } else {
                r[v] = data[v]
            }
        });
        // Load records
        me.form.reset();
        me.form.setValues(r);
    },
    //
    getFormData: function() {
        var me = this,
            fields = me.form.getFields().items,
            f, field, data, name,
            fLen = fields.length,
            values = {};
        for(f = 0; f < fLen; f++) {
            // hack to get instance of .TreeCombo class
            if(Ext.String.endsWith(fields[f].xtype, '.TreeCombo')) {
                field = me.fields[f];
            } else {
                field = fields[f];
            }
            if(field.inEditor) {
                // Skip grid inline editors
                // WARNING: Will skip other inline editors
                continue;
            }
            data = field.getModelData();
            if(Ext.isObject(data)) {
                name = field.getName();
                if(data.hasOwnProperty(name)) {
                    values[name] = data[name];
                }
            }
        }
        return values;
    },
    //
    getFormField: function(name) {
        var me = this,
            fields = me.form.getFields().items,
            fLen = fields.length,
            f, field;
        for(f = 0; f < fLen; f++) {
            f = fields[f];
            if(f.name === name) {
                return f
            }
        }
        return null
    },
    //
    cleanData: function(v) {

    },
    //
    setTitle: function(title) {
        var me = this;
        me.formTitle.setHtml(title)
    }
});
