!function(){var a=Handlebars.template,n=NOC.templates.fm_alarm=NOC.templates.fm_alarm||{};n.Data=a({1:function(a,n,t,l,r){var e=a.lambda,m=a.escapeExpression;return"    <tr>\n        <td><b>"+m(e(null!=n?n[0]:n,n))+"</b></td>\n        <td>"+m(e(null!=n?n[1]:n,n))+"</td>\n    </tr>\n"},compiler:[7,">= 4.0.0"],main:function(a,n,t,l,r){var e;return'<table border="0">\n    <tr><th colspan="2">Alarm Variables</th></tr>\n'+(null!=(e=t.each.call(null!=n?n:{},null!=n?n.vars:n,{name:"each",hash:{},fn:a.program(1,r,0),inverse:a.noop,data:r}))?e:"")+"</table>\n"},useData:!0})}();Ext.define("NOC.fm.alarm.templates.Data", {});