# Правила реагирования на алерты

| Алертгруппа      	| Имя  алерта                   	| Описание                                                                                             	 | Алгоритм  обработки алерта 	|
|------------------	|-------------------------------	|--------------------------------------------------------------------------------------------------------|----------------------------	|
| blackbox.rules   	| EndpointDown                  	| -                                                                                                    	 | -                          	|
| blackbox.rules   	| SSLCertExpiringSoon           	| Срок действия SSL для (имя домена) истекает через (кол-во дней)                                      	 | -                          	|
| clickhouse.rules 	| ClickhouseInsertRateLow       	| На хосте у кликхауса низкая скорость вставки                                                         	 | -                          	|
| clickhouse.rules 	| DiskSpacePredictionCH         	| Загрузка места на диске Кликхауса превысит 97% через 3 дня                                           	 | -                          	|
| consul.rules     	| ConsulServicesCountDecrease   	| Более 50% экземпляров не работают                                                                    	 | -                          	|
| infra.rules      	| CPUUsageHigh                  	| Загрузка процессора превышает 90%                                                                    	 | -                          	|
| infra.rules      	| MemoryUsageHigh               	| Использование памяти превышает 90%                                                                   	 | -                          	|
| infra.rules      	| SwapUsageHigh                 	| Загрузка Swap превышает 90%                                                                          	 | -                          	|
| infra.rules      	| LoadAverageHigh               	| Высокий ЛА                                                                                           	 | -                          	|
| infra.rules      	| DiskSpaceUsage                	| Загрузка места на диске превышает 90%                                                                	 | -                          	|
| infra.rules      	| DiskInodesUsageHigh           	| Загрузка айнод на диске превышает 90%                                                                	 | -                          	|
| infra.rules      	| SystemReboot                  	| Перезагрузка системы                                                                                 	 | -                          	|
| liftbridge.rules 	| CorrelatorQueueTooLarge       	| Алармы сервиса correlator выстраиваются в очередь более чем на 1000 в течение как минимум пяти минут 	 | -                          	|
| liftbridge.rules 	| ClassifierQueueTooLarge       	| Алармы сервиса classifier выстраиваются в очередь более чем на 1000 в течение как минимум пяти минут 	 | -                          	|
| liftbridge.rules 	| UncommitedMessagesTooMuch     	| Слишком много незафиксированных сообщений в LB                                                       	 | -                          	|
| liftbridge.rules 	| StreamInvertedValue           	| Поток инвертированного значения в LB                                                                 	 | -                          	|
| mongo.rules      	| MongoClasterServerCountChange 	| Член кластера Mongodb, вероятно, мертв                                                               	 | -                          	|
| mongo.rules      	| MongoConnectionLow            	| Mongodb на хосте, вероятно, мертв                                                                    	 | -                          	|
| mongo.rules      	| MongoReplicationLag           	| Mongodb на хосте устарел                                                                             	 | -                          	|
| noc.rules        	| FMNoEscalations               	| В течение длительного периода времени не происходит никаких обострений                               	 | -                          	|
| noc.rules        	| FmTooManyAlerts               	| Высокий процент аварийных сигналов                                                                   	 | -                          	|
| noc.rules        	| LateTasksOnPool               	| Задержка тасок на 10 минут в пуле                                                                    	 | -                          	|
| noc.rules        	| LateTasksScheduler            	| Очередь тасок шедулера перегружена                                                                   	 | -                          	|
| noc.rules        	| HighTracesPerSecond           	| Слишком много трейсов от не активатора                                                               	 | -                          	|
| postgres.rules   	| PostgresqlDeadlocksHigh       	| Обнаружены дедлоки на посгресе                                                                       	 | -                          	|
| postgres.rules   	| PostgresqlBackendsLow         	| Слишком мало серверных процессов подключенных к базе посгрес                                         	 | -                          	|
| prometheus.rules 	| ServiceDown                   	| Прометеус не может соединиться с (имя сервиса)                                                       	 | -                          	|
| self.rules       	| DeadMansSwitch                	| -                                                                                                    	 | -                          	|