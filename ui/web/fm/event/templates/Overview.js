!function(){var e=Handlebars.template,n=NOC.templates.fm_event=NOC.templates.fm_event||{};n.Overview=e({compiler:[7,">= 4.0.0"],main:function(e,n,a,l,t){var s,u=null!=n?n:{},r=a.helperMissing,p="function",b=e.escapeExpression;return"<b>"+b((s=null!=(s=a.subject||(null!=n?n.subject:n))?s:r,typeof s===p?s.call(u,{name:"subject",hash:{},data:t}):s))+"</b><br/>\n<pre>"+b((s=null!=(s=a.body||(null!=n?n.body:n))?s:r,typeof s===p?s.call(u,{name:"body",hash:{},data:t}):s))+"</pre>\n"},useData:!0})}();Ext.define("NOC.fm.event.templates.Overview", {});