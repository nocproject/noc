###
	Корневой виджет приложения.
###
Ext.define 'Report.view.root.Main',
	extend: 'Ext.panel.Panel'
	xtype: 'rootMain'

	requires: [
		'Report.view.root.AddDashboard'
		'Report.view.root.NocToolbar'
		'Report.view.root.TabPanel'
	]
	
	items: [
		{
			itemId: 'tabPanel'
			xtype: 'rootTabPanel'
			listeners:
				afterrender: () ->
					@getTabBar().add [
						{
							xtype: 'component'
							flex: 1
						},
						{
							itemId: 'addDashboard'
							xtype: 'rootAddDashboard'
							margin: '2 10 2 2'
						}
					]
		}
	]

	dockedItems: [
		{
			itemId: 'nocToolbar'
			xtype: 'rootNocToolbar'
			docked: 'top'
		}
	]