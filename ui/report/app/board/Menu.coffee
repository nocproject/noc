Ext.define 'Report.board.Menu',
	extend: 'Ext.toolbar.Toolbar'
	xtype: 'boardMenu'
	controller: 'boardMenu'

	items: [
		{
			xtype: 'segmentedbutton'
			items: [
				{
					text: 'Сегодня'
					handler: 'currentDay'
				}
				{
					text: 'Вчера'
					handler: 'yesterday'
				}
				{
					text: 'Неделя'
					handler: 'week'
				}
				{
					text: 'Месяц'
					handler: 'month'
				}
				{
					text: 'Квартал'
					handler: 'quarter'
				}
				{
					text: 'Год'
					handler: 'year'
				}
			]
		}
		{
			xtype: 'tbspacer'
			width: 20
		}
		{
			itemId: 'from'
			xtype: 'datefield'
			fieldLabel: 'с'
			labelWidth: 10
			maxValue: new Date
			listeners:
				change: 'dateFrom'
		}
		{
			xtype: 'tbspacer'
			width: 20
		}
		{
			itemId: 'to'
			xtype: 'datefield'
			fieldLabel: 'по'
			labelWidth: 20
			maxValue: new Date
			listeners:
				change: 'dateTo'
		}
		'->'
		{
			xtype: 'button'
			text: 'Добавить виджет'
			handler: 'addWidget'
		}
	]