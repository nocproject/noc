!function(){var t=Handlebars.template,n=NOC.templates.main_desktop=NOC.templates.main_desktop||{};n.About=t({1:function(t,n,e,i,l){var a;return'<div style="font-size: 12pt">System ID: '+t.escapeExpression((a=null!=(a=e.system_id||(null!=n?n.system_id:n))?a:e.helperMissing,"function"==typeof a?a.call(null!=n?n:{},{name:"system_id",hash:{},data:l}):a))+"</div>\n"},3:function(t,n,e,i,l){return'<div style="font-size: 12pt">Unregistred system</div>\n'},compiler:[7,">= 4.0.0"],main:function(t,n,e,i,l){var a,s,o=null!=n?n:{},r=e.helperMissing,p="function",d=t.escapeExpression;return'<img src="/ui/web/img/logo_black.svg" style="width: 100px; height: 100px; padding: 8px; float: left"></img>\n<div style="font-size: 16pt; font-weight: bold">NOC '+d((s=null!=(s=e.version||(null!=n?n.version:n))?s:r,typeof s===p?s.call(o,{name:"version",hash:{},data:l}):s))+'</div>\n<div style="font-size: 12pt; font-style: italic">'+d((s=null!=(s=e.installation||(null!=n?n.installation:n))?s:r,typeof s===p?s.call(o,{name:"installation",hash:{},data:l}):s))+"</div>\n"+(null!=(a=e.if.call(o,null!=n?n.system_id:n,{name:"if",hash:{},fn:t.program(1,l,0),inverse:t.program(3,l,0),data:l}))?a:"")+'<div style="">Copyright &copy; '+d((s=null!=(s=e.copyright||(null!=n?n.copyright:n))?s:r,typeof s===p?s.call(o,{name:"copyright",hash:{},data:l}):s))+"</div>\n<a href='http://nocproject.org/' target='_'>nocproject.org</a>\n"},useData:!0})}();Ext.define("NOC.main.desktop.templates.About", {});