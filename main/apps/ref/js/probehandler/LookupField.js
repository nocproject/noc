//---------------------------------------------------------------------
// NOC.main.ref.probehandler.LookupField
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.ref.probehandler.LookupField");

Ext.define("NOC.main.ref.probehandler.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.ref.probehandler.LookupField",
    requires: ["NOC.main.ref.probehandler.Lookup"],
    tpl: [
        '<tpl for=".">',
            '<div class="x-boundlist-item">',
                '{label}<tpl if="solution"> <i>({solution})</i></tpl>',
                '<tpl if="tags.length &gt; 0">',
                    '<tpl for="tags">',
                        ' <span class="x-display-tag">{.}</span>',
                    '</tpl>',
                '</tpl>',
                '<div class="item-description">{description}</div>',
            '</div>',
        '</tpl>'
    ]
});
