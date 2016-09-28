###
	Тулбар управления Noc.
###
Ext.define 'Report.view.root.NocToolbar',
	extend: 'Ext.toolbar.Toolbar'
	xtype: 'rootNocToolbar'
	cls: 'noc-menu'

	items: [
		{
			xtype: 'tbtext'
			text: 'NOC | Отчеты'
		}
		'->'
		{
			itemId: 'userButton'
			xtype: 'button'
			iconCls: 'x-fa fa-user'
			text: 'empty'
		}
	]