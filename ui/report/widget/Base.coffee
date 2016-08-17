Ext.define 'Report.widget.Base',
	extend: 'Ext.panel.Panel'

	config:
		settingsType: ''

	tools: [
		{
			type: 'gear',
			callback: 'showSettings'
		}
	]

	showSettings: () ->
		Ext.create @getSettingsType(), {widget: @}