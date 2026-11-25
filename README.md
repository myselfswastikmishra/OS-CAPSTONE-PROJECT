# OS Resource Monitoring & Alert System

An integrated Python application with Bash/Windows launchers that monitors CPU, RAM, disk and processes, records timestamped metrics, generates threshold alerts, charts and a system-health report.


## Features
- CPU utilization, RAM utilization/available memory, disk usage and free space.
- Process count, process snapshots and top CPU/memory process lists.
- Configurable warning and critical thresholds (`data/config.json`).
- Timestamped metrics, alerts and process snapshots stored in CSV.
- Activity logging in `logs/activity.log`.
- Graphs from collected history and summary report with recommendations.
- Interactive menu plus command-line actions.


## Requirements
Python 3.9+ recommended. Dependencies: `psutil`, `matplotlib`.


## Windows quick start
1. Extract the project ZIP.
2. Open the folder.
3. Double-click `run.bat` or run in Command Prompt:
   ```bat
   python -m pip install -r requirements.txt
   python src\monitor.py
   ```

## Linux/macOS quick start
```bash
chmod +x run.sh
./run.sh
```

## Commands
```bash
python src/monitor.py                 # interactive menu
python src/monitor.py --once           # single metric snapshot
python src/monitor.py --monitor       # continuous monitoring (Ctrl+C stops)
python src/monitor.py --report        # generate report
python src/monitor.py --graphs        # graphs from stored history
```

On Windows, replace `python` with `py` if needed, or use `run.bat`.

## Menu
1. Live dashboard
2. Collect one snapshot
3. Process monitoring
4. Top CPU processes
5. Top memory processes
6. Alert history
7. Generate report
8. Generate graphs
9. System health analysis
10. Configure thresholds
11. Show data file locations
0. Exit

## Thresholds
Defaults are CPU/RAM warning 75%, critical 90%; disk warning 80%, critical 95%. Edit `data/config.json` or use the menu to configure them. Critical alerts are logged and appended to `output/alerts.csv`.


## Output files
- `output/metrics.csv`: timestamped system metric history
- `output/alerts.csv`: threshold alerts
- `output/processes.csv`: process snapshots
- `output/system_report.txt`: text report with min/max/average values and recommendations
- `output/cpu_history.png`, `memory_history.png`, `disk_history.png`, `resource_comparison.png`: plots
- `logs/activity.log`: activity log

## Testing
```bash
python -m unittest discover -s tests -v
```

## Notes
- Disk monitoring uses the configured `disk_path`; by default it monitors the system drive on Windows and `/` on Linux/macOS.
- Some process details may be unavailable due to permissions; the program skips inaccessible processes.
- CPU readings are sampled with a short interval; very brief spikes may not be captured.
- Graphs need at least two recorded metric samples.
