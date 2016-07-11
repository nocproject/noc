//---------------------------------------------------
// Ext.ux.form.GeoField
//     ExtJS4 form field
//     to edit longitude/latitude pairs
//---------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------
Ext.define("Ext.ux.form.GeoField", {
    extend: "Ext.form.field.Base",
    alias: "widget.geofield",
    requires: ["Ext.form.field.Base"],

    width: 270,
    fieldSubTpl: [
        "<div class='noc-geo-wrap'>",
        "<div class='noc-geo-lat'></div>",
        "<div class='noc-geo-lon'></div>",
        "</div>",
        {
            compiled: true,
            disableFormats: true
        }
    ],

    validationEvent: "change",

    initComponent: function() {
        if(!Ext.isDefined(this.value))
            this.value = [0, 0];
        this.callParent();
    },

    initEvents: function() {
        this.callParent();
        if(this.validationEvent != false && this.validationEvent != "blur") {
            this.mon(this, this.validationEvent, this.validate, this,
                     {buffer: this.validationDelay});
        }
    },

    onRender: function(ct, position) {
        this.callParent([ct, position]);
        // Create inputs
        this.hiddenField = this.el.insertSibling({
            tag: "input",
            type: "hidden",
            name: this.name || this.id,
            id: this.id + "hidden"
            }, "before", true);
        this.lonField = Ext.createByAlias("widget.numberfield", {
            renderTo: Ext.query(".noc-geo-lat", this.el.dom)[0],
            width: 80,
            allowDecimals: true,
            decimalPrecision: 4,
            minValue: -180.0,
            maxValue: 179.9999,
            enableKeyEvents: true,

            listeners: {
                scope: this,
                keyup: this.onFieldsChanged
            }
        });
        this.latField = Ext.createByAlias("widget.numberfield", {
            renderTo: Ext.query(".noc-geo-lon", this.el.dom)[0],
            width: 80,
            allowDecimals: true,
            decimalPrecision: 4,
            enableKeyEvents: true,
            minValue: -90.0,
            maxValue: 89.9999,
            listeners: {
                scope: this,
                keyup: this.onFieldsChanged
            }
        });
        if(this.value)
            this.setValue(this.value);
    },

    getValue: function() {
        return this.value;
    },

    getRawValue: function() {
        return this.value;
    },

    onFieldsChanged: function() {
        this.value = [
            this.lonField.getValue(),
            this.latField.getValue()
        ];
        this.hiddenField.value = this.value;
        this.fireEvent("change", this.value);
    },

    setValue: function(v) {
        var setFn = function(v) {
            this.lonField.setValue(v[0]);
            this.latField.setValue(v[1]);
            this.hiddenField.value = v;
        };

        if(this.rendered)
            setFn.call(this, v);
        else
            this.on({
                afterrender: Ext.bind(setFn, this, [v]),
                scope: this,
                single: true
            });
    },

    validateValue: function(value) {
        if(this.allowBlank !== false) {
            return true;
        } else {
            if(Ext.isDefined(value) && value != "") {
                this.clearInvalid();
                return true;
            } else {
                this.markInvalid(this.blankText);
                return false;
            }
        }
    }
});
