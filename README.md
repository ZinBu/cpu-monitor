# cpu-monitor

A small utility for viewing CPU load/temperature through the tray icon.
It is possible to change colors =)


### Python 3.11

### Launch via `pip' (unstable)

    pip install -r requirements.txt
    python main.py

### Launch via `poetry`

    poetry shell  # (optional)
    poetry install
    poetry run python main.py


### Creating a script to run

    make runner

Running the script (can be added to the startup):
    
    sh cpu_monitor.sh
