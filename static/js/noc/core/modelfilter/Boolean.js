//---------------------------------------------------------------------
// NOC.core.modelfilter.Boolean
// Boolean model filter
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.modelfilter.Boolean");

Ext.define("NOC.core.modelfilter.Boolean", {
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
                                this._value = {
                                    "all": null,
                                    "yes": true,
                                    "no": false
                                }[radio.inputValue];
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
                            boxLabel: "Yes",
                            inputValue: "yes"
                        },
                        {
                            boxLabel: "No",
                            inputValue: "no"
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
