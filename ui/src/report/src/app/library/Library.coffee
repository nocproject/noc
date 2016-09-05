Ext.define 'Report.library.Library',
	extend: 'Ext.window.Window'
	xtype: 'library'
	controller: 'library'
	cls: 'library'

	title: 'Библиотека виджетов'

	layout: 'hbox'
	width: 900
	height: 550
	bodyPadding: 10
	closeAction: 'hide'

	defaults:
		padding: 5

	items: [
		{
			itemId: 'groups'
			xtype: 'dataview'
			itemTpl: '<span class="item">{groupName}</span>'
			flex: 1,
# TODO DEMO
			store:
				fields: ['groupName']
				data: [
					{groupName: 'Имя группы 1'}
					{groupName: 'Имя группы 2'}
					{groupName: 'Имя группы 3'}
					{groupName: 'Имя группы 4'}
					{groupName: 'Имя группы 5'}
					{groupName: 'Свои виджеты'}
				]
			listeners:
				afterrender: () -> @select 0
		}
		{
			itemId: 'widgets'
			xtype: 'dataview'
			itemTpl: '<span class="item">{name}</span>'
			flex: 1
# TODO DEMO
			store:
				fields: ['name']
				data: [
					{name: 'Имя виждета 1'}
					{name: 'Имя виждета 2'}
					{name: 'Имя виждета 3'}
					{name: 'Имя виждета 4'}
					{name: 'Имя виждета 5'}
					{name: 'Имя виждета 6'}
					{name: 'Имя виждета 7'}
					{name: 'Имя виждета 8'}
					{name: 'Имя виждета 9'}
					{name: 'Имя виждета 10'}
				]
			listeners:
				afterrender: () -> @select 3
		}
		{
			xtype: 'container'
			layout: 'vbox'
			height: '100%'
			flex: 2
			items: [
				{
					itemId: 'description'
					xtype: 'component'
					cls: 'widget-description'
					width: '100%'
					flex: 1
					tpl:
					'
					<div class="title">{name}</div>
					<div class="description">{description}</div>
					'
# TODO DEMO
					data:
						name: 'Имя виджета'
						description: '
							Описание виджета, который отображает
							данные в виде таблицы или в виде графика,
							получая нужные данные из одного или нескольких
							источников, с фильтрацией и разными иными полезными
							функциями, но достаточно минималистично для одного
							виждета, отображающего один тип показателей.
						'
				}
				{
					xtype: 'container'
					width: '100%'
					layout:
						type: 'hbox'
						pack: 'end'
					items:
						xtype: 'button'
						text: 'Добавить'
						width: 100
						handler: 'addWidget'
				}
			]
		}
	]