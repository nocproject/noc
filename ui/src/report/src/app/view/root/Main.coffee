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
					@getTabBar().add({
						itemId: 'addDashboard'
						xtype: 'rootAddDashboard'
					})
		}
	]

	dockedItems: [
		{
			itemId: 'nocToolbar'
			xtype: 'rootNocToolbar'
			docked: 'top'
		}
	]