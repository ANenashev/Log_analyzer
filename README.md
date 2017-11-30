# Log analyzer
Скрипт анализирует файлы логов интерфейса веб-сервиса и составляет файл отчета, в который включены REPOR_SIZE самых медленных запросов.

Конфигурация по умолчанию:

* REPORT_SIZE: 1000 - количество строк в отчете
* REPORT_DIR: "./reports" - папка с отчетами
* LOG_DIR: "./log" - папка с логами
* LOG_PATH: "./log_analyzer.log" - файл логов анализатора
* TS_PATH: "./log_nalyzer.ts" - файл timestamp

Для запуска нужно ввести python log_analyzer.py. Можно указать файл конфигурации в параметре --config: python log_analyzer.py --config "path/to/config.file".

Для запуска тестов нужно ввести python test_log_analyzer.py.
