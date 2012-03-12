//---------------------------------------------------------------------
// NOC.core.modelfilter.AFI
// AFI model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.AFI");

Ext.define("NOC.core.modelfilter.AFI", {
    extend: "NOC.core.modelfilter.Base",

    initComponent: function() {
        Ext.apply(this, {
            items: [
                {
                    xtype: "radiogroup",
                    columns: 3,
                    defaults: {
                        name: this.name,
                        scope: this,
                        handler: function(radio, checked) {
                            if(checked) {
                                var v = radio.inputValue;
                                if (v == "all")
                                    this._value = null;
                                else
                                    this._value = v;
                                this.onChange();
                            }
                        }
                    },
                    items: [
                        {
                            boxLabel: "All",
                            inputValue: "all",
                            checked: true
                        },
                        {
                            boxLabel: "IPv4",
                            inputValue: "4"
                        },
                        {
                            boxLabel: "IPv6",
                            inputValue: "6"
                        }
                    ]
                }
            ]
        });
        this.callParent();
        this.radiogroup = this.items.items[0];
        this._value = null;
    },

    getFilter: function() {
        var r = {};
        if(this._value !== null)
            r[this.name] = this._value;
        return r;
    }
});
