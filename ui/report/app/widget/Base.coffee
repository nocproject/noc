Ext.define 'Report.widget.Base',
	extend: 'Ext.panel.Panel'
	xtype: 'widgetBase'

	title: 'Виджет'
	cls: 'widget-base'
	shadow: true
	# draggable: true TODO ждем момента старта полной разработки
	bodyPadding: 12
	width: 0
	height: 0

	tools: [
		{
			type: 'gear',
			# TODO callback: 'showSettings'
		}
	]

	showSettings: () ->
		Ext.create @getSettingsType(), {widget: @}