//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.widget.Check");

Ext.define("NOC.sa.discoveredobject.widget.Check", {
    extend: "Ext.form.field.Base",
    alias: "widget.checkfield",
    layout: "fit",
    combineErrors: true,
    msgTarget: "side",
    fieldSubTpl: [
        "<div></div>",
    ],
    afterRender: function() {
        this.createForm();
        this.callParent(arguments);
    },
    reset: function() {
        this.callParent(arguments);
        this.value = this.rawValue = [];
        Ext.each(this.form.query("form"), function(form) {
            this.form.remove(form);
        }, this);
        this.form.add(this.createRow());
    },
    getValue: function() {
        return this.value || [];
    },
    setValue: function(values) {
        Ext.defer(function() {
            Ext.each(this.form.query("form"), function(form) {
                this.form.remove(form);
            }, this);
            if(Ext.isEmpty(values)) {
                this.form.add(this.createRow());
            } else {
                Ext.each(values, function(value) {
                    var v = value.split("__"),
                        row = this.form.add(this.createRow());

                    switch(v.length) {
                        case 3: {
                            row.getForm().setValues({
                                name: value.split("__")[0],
                                port: value.split("__")[1],
                                value: value.split("__")[2],
                            });
                            break;
                        }
                        case 2: {
                            row.getForm().setValues({
                                name: value.split("__")[0],
                                value: value.split("__")[1],
                            });
                            break;
                        }
                    };
                }, this);
            }
        }, 100, this);
    },
    createForm: function() {
        var me = this;

        me.form = Ext.create("Ext.panel.Panel", {
            renderTo: me.bodyEl,
            border: false,
            width: "100%",
            layout: {
                type: "vbox",
                pack: "bottom"
            },
            items: [
                {
                    xtype: "button",
                    glyph: NOC.glyph.plus,
                    handler: function() {
                        me.form.add(me.createRow());
                    }
                },
                me.createRow()
            ],
            listeners: {
                change: function() {
                    var value = me.form.getValues();

                    me.rawValue = value;
                    me.fireEvent("change", me, value);
                },
                add: function() {
                    me.fireEvent("updateLayout");
                },
                remove: function() {
                    me.fireEvent("updateLayout");
                }
            }
        });
    },
    createRow: function() {
        var me = this;

        return Ext.create({
            xtype: "form",
            border: false,
            layout: "hbox",
            padding: "5 0 0 0",
            defaults: {
                margin: "0 5 0 0",
                uiStyle: undefined,
            },
            items: [
                {
                    xtype: "combobox",
                    name: "name",
                    emptyText: __("check"),
                    editable: false,
                    displayField: "label",
                    allowBlank: false,
                    width: 100,
                    store: {
                        xtype: "store",
                        autoLoad: true,
                        proxy: {
                            type: "ajax",
                            url: "/main/ref/check/lookup/",
                            reader: {
                                type: "json",
                                rootProperty: "data"
                            }
                        }
                    },
                    listeners: {
                        change: function(combo, value) {
                            var record = combo.getStore().findRecord(combo.valueField, value),
                                form = combo.up("form");

                            form.down("numberfield").setDisabled(!record.get("has_port"));
                            me.setValues(form);
                        }
                    }
                },
                {
                    xtype: "numberfield",
                    name: "port",
                    emptyText: "1-65536",
                    maxValue: 65536,
                    minValue: 1,
                    width: 75,
                    checkChangeBuffer: 250,
                    disabled: true,
                    listeners: {
                        change: function(numberfield) {
                            me.setValues(numberfield.up("form"));
                        }
                    }
                },
                {
                    xtype: "checkbox",
                    name: "value",
                    getSubmitValue: function() {
                        return this.checked ? true : false;
                    },
                    listeners: {
                        change: function(checkbox) {
                            me.setValues(checkbox.up("form"));
                        }
                    }
                },
                {
                    xtype: "button",
                    glyph: NOC.glyph.minus,
                    handler: function() {
                        var row = this.up("form");

                        row.up().remove(row);
                        me.fireEvent("updateLayout");
                    }
                }
            ],
        });
    },
    setValues: function(form) {
        var me = this,
            forms = me.form.query("form");

        for(var i = 0; i < forms.length; i++) {
            if(!form.isValid() && form.isDirty()) {
                return;
            }
        }
        me.value = me.rawValue = Ext.Array.map(
            Ext.Array.filter(forms, function(form) {
                return form.isValid();
            }), function(form) {
                var values = form.getValues();
                return Ext.String.format("{0}{1}__{2}", values.name, values.port ? "__" + values.port : "", values.value);
            });
        me.fireEvent("change", me, me.value);
    },
});