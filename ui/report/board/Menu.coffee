Ext.define 'Report.board.Menu',
	extend: 'Ext.toolbar.Toolbar'
	xtype: 'boardMenu'

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
			itemId: 'from'
			xtype: 'datefield'
			fieldLabel: 'с'
			listeners:
				change: 'dateFrom'
		}
		{
			itemId: 'to'
			xtype: 'datefield'
			fieldLabel: 'по'
			listeners:
				change: 'dateTo'
		}
		'->'
		{
			xtype: 'button'
			text: 'Добавить виджет'
		}
	]

	currentDay: () ->
		@sliceTo new Date

    yesterday: () ->
		@sliceToMargin 'DAY', 1

	week: () ->
		@sliceToMargin 'DAY', 7

	month: () ->
		@sliceToMargin 'MONTH', 1

	quarter: () ->
		@sliceToMargin 'MONTH', 7

	year: () ->
		@sliceToMargin 'YEAR', 1

	dateFrom: (widget, value) ->
		@slice value, @toFieldValue()

	dateTo: (widget, value) ->
		@slice @fromFieldValue(), value

	privates:

		sliceDateToMargin: (type, count) ->
			@sliceTo @dateMargin type, count

		sliceDateTo: (to) ->
			@slice new Date, to

		slice: (from, to) ->
			Report.data.Mediator.sliceDateStream from, to

		fromFieldValue: () ->
			@down('#to').getValue()

		toFieldValue: () ->
			@down('#from').getValue()

		dateMargin: (type, count) ->
			Ext.Date.add new Date, Ext.Date[type], -count
