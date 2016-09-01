Ext.define 'Report.NocMenu',
	extend: 'Ext.toolbar.Toolbar'
	xtype: 'nocMenu'
	cls: 'noc-menu'

	items: [
		{
			xtype: 'tbtext'
			text: 'NOC | Отчеты'
		}
		'->'
		{
			itemId: 'userButton'
			xtype: 'button',
			iconCls: 'x-fa fa-user'
			text: 'admin'
		}
	]

	setUserName: (name) ->
		@up('#userButton').setText name