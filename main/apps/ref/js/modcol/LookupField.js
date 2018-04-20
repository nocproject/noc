//---------------------------------------------------------------------
// NOC.main.ref.modcol.LookupField
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.ref.modcol.LookupField");

Ext.define("NOC.main.ref.modcol.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.ref.modcol.LookupField",
    requires: ["NOC.main.ref.modcol.Lookup"],
    tpl: [
        '<tpl for=".">',
            '<div class="x-boundlist-item">',
                '{label}<br/>',
                '<div class="item-description">',
                    '<tpl if="table">Table: {table}</tpl>',
                    '<tpl if="collection">Collection: {collection}</tpl>',
                '</div>',
            '</div>',
        '</tpl>'
    ],
    uiStyle: "large"
});
