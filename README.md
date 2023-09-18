# cpu-monitor

Маленькая утилитка для просмотра нагрузки/температуры ЦП через значок трея. 
Есть возможность менять цвета =)


### Python 3.11

### Запуск через `pip` (unstable)

    pip install -r requirements.txt
    python main.py

### Запуск через `poetry`

    poetry shell  # (optional)
    poetry install
    poetry run python main.py


### Создания скрипта для запуска

    make runner

Запуск скрипта (можно добавить в автозагрузку):
    
    sh cpu_monitor.sh
