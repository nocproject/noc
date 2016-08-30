Ext.define 'Report.board.Board',
	extend: 'Ext.panel.Panel'
	xtype: 'board'
	controller: 'board'
	requires: [
		'Ext.ux.layout.ResponsiveColumn'
	    'Report.board.Menu'
		'Report.board.BoardController',
		'Report.widget.Base'

		# TODO DEMO
		'Ext.chart.axis.Numeric'
		'Ext.chart.axis.Category'
		'Ext.chart.series.Area'
	]

	layout: {
		type: 'hbox'
		align: 'center'
		pack: 'center'
	}
	
	tbar:
		xtype: 'boardMenu'
		listeners:
			afterrender: 'dotting'
			addWidget: 'showWidgetLibrary'

	# TODO DEMO
	items: [
		{
			xtype: 'widgetBase'
			title: 'Виджет 1'
			boardWidth: 1
			boardHeight: 1
			layout: 'fit'
			items:
				xtype: 'grid'
				columns: [
					{
						text: 'ID'
						dataIndex: 'id'
						flex: 1
					}
					{
						text: 'Состояние'
						dataIndex: 'name'
						flex: 1
						renderer: (value) ->
							"<b style='color: green'>#{value}</b>"
					}
				]
				store:
					fields: ['id', 'name']
					data: [
						{id: '5732', name: 'Активно'}
						{id: '5736', name: 'Активно'}
						{id: '5782', name: 'Активно'}
						{id: '5799', name: 'Активно'}
					]
		}
		{
			xtype: 'widgetBase'
			title: 'Виджет 2'
			boardWidth: 1
			boardHeight: 2
			layout: 'fit'
			items:
				xtype: 'grid'
				columns: [
					{
						text: 'ID'
						dataIndex: 'id'
						flex: 1
					}
					{
						text: 'Нагрузка'
						dataIndex: 'load'
						flex: 1
						renderer: (value) ->
							if value > 70
								"<b style='color: red'>#{value}</b>"
							else
								value
					}
				]
				store:
					fields: ['id', 'load']
					data: [
						{id: 'a34523', load: 50}
						{id: 'a3360', load: 30}
						{id: 'b3542', load: 5}
						{id: 'a3520', load: 7}
						{id: 'c32211', load: 69}
						{id: 'a2354', load: 99}
						{id: 'b25243', load: 15}
						{id: 'a23208', load: 77}
						{id: 'a9079', load: 30}
						{id: 'a7600', load: 25}
						{id: 'a70609', load: 44}
						{id: 'a60825', load: 32}
						{id: 'a73232', load: 25}
						{id: 'a70099', load: 44}
						{id: 'a00787', load: 32}
						{id: 'a20031', load: 99}
						{id: 'd2235', load: 17}
					]
		}
		{
			xtype: 'widgetBase'
			title: 'Виджет 3'
			boardWidth: 2
			boardHeight: 1
			layout: 'fit'
			items:
				xtype: 'grid'
				columns: [
					{
						text: 'ID'
						dataIndex: 'id'
					}
					{
						text: 'IP'
						dataIndex: 'ip'
					}
					{
						text: 'hash'
						dataIndex: 'hash'
						flex: 1
					}
				]
				store:
					fields: ['id', 'ip', 'hash']
					data: [
						{id: '5732', ip: '77.88.55.77', hash: 'VrlSCusrPKt4VG9XFd1.MOkuoIAyK5SUuAdnxAtBqF2k6Lwo9LlaS'}
						{id: '5782', ip: '173.194.122.206', hash: 'O1t4LWANKwx6xPKhbV6vRuX7X70N9wc1LcZaPFluqF8ckwE3KILvC'}
						{id: '6400', ip: '104.20.19.80', hash: 'l1RRg2/dQaOYB3afJCRaeOd3gb/okOrDRYCXkwBSBMxjBmasdnSia'}
						{id: '6401', ip: '104.23.131.83', hash: 'Lq4VwO9tVjYGO1t8ydjVOueS5jkaifL3CCYbKQgiRqSE0PL/vpwni'}
					]
		}
		{
			xtype: 'widgetBase'
			title: 'Виджет 4'
			boardWidth: 1
			boardHeight: 1
			layout: 'fit'
			items:
				xtype: 'cartesian'
				store:
					fields: ['name', 'data1', 'data2', 'data3']
					data: [
						{
							name: '10'
							data1: 10
							data2: 12
							data3: 14
						}
						{
							name: '11'
							data1: 7
							data2: 8
							data3: 16
						}
						{
							name: '12'
							data1: 5
							data2: 2
							data3: 14
						}
						{
							name: '13'
							data1: 2
							data2: 14
							data3: 6
						}
						{
							name: '14'
							data1: 27
							data2: 38
							data3: 36
						}
					]
				axes: [
					{
						type: 'numeric'
						position: 'left'
						fields: ['data1']
						grid: true,
						minimum: 0
					}
					{
						type: 'category'
						position: 'bottom'
						fields: ['name']
					}
				]
				series:
					type: 'area'
					subStyle:
						fill: ['#0A3F50', '#30BDA7', '#96D4C6']
					xField: 'name'
					yField: ['data1', 'data2', 'data3']
		}
	]