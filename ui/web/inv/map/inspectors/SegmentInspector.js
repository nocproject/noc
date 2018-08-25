//---------------------------------------------------------------------
// Segment inspector
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.inspectors.SegmentInspector");

Ext.define("NOC.inv.map.inspectors.SegmentInspector", {
    extend: "NOC.inv.map.inspectors.Inspector",
    title: __("Segment Inspector"),
    inspectorName: "segment",

    tpl: [
        '<b>Name:&nbsp;</b>{name}<br/>',
        '<tpl if="description">',
            '<b>Description:&nbsp;</b><br/>{description}<br/>',
        '</tpl>',
        '<tpl if="objects">',
            '<b>Objects:&nbsp;</b>{objects}',
        '</tpl>'
    ]
});
