# Project Report: OS Resource Monitoring & Alert System

**Course:** Operating Systems  
**Project Type:** Python + Bash integrated application  

## Abstract
This project implements a system-monitoring utility that samples operating-system CPU, memory, disk and process information. The collector records timestamped data in CSV format, evaluates configurable warning/critical thresholds, stores alerts and provides graphs and a text performance report. The application supports interactive use and command-line automation.

## Problem Statement
Resource saturation can cause slowdowns and instability. Users need a straightforward way to observe resource utilization, identify resource-intensive processes, retain history, detect threshold crossings and receive actionable guidance.

## Objectives
- Monitor CPU, RAM, disk and running processes.
- Persist timestamped measurements.
- Trigger threshold-based warnings and critical alerts.
- Analyze history and visualize trends.
- Provide recommendations based on current conditions.
- Integrate Python monitoring logic with a Bash launcher.

## Design
The collector uses `psutil` for OS telemetry. A metrics layer normalizes readings into a structured record; the threshold engine classifies each resource as OK, WARNING or CRITICAL; storage writes CSV rows; analytics generates plots and a text report; the menu coordinates user actions. Bash provides a dependency check/launcher on Linux and a batch launcher is included for Windows.

## Metrics
CPU percentage; RAM total, used, available and percent; disk total, used, free and percent; process count; network bytes sent/received; process PID/name/username/CPU/RSS memory.

## Threshold Logic
For each resource, the warning threshold and critical threshold are configurable. Values below warning are OK; values at or above warning are WARNING; values at or above critical are CRITICAL. The critical threshold takes precedence.

## Testing
Unit tests cover classification boundaries, alert generation for warning/critical cases, and health recommendations. Additional manual checks include a single collection run, continuous sampling interrupted with Ctrl+C, CSV output inspection, graph generation with multiple samples, report generation, invalid menu choices and threshold configuration.

## Limitations
Sampling may miss short spikes. Process telemetry may be restricted by OS permissions. Disk usage is a capacity snapshot rather than a disk I/O throughput measure. Graph generation requires at least two samples. This project monitors but does not automatically terminate processes or modify system settings.

## Conclusion
The application provides a modular and practical demonstration of OS process, CPU, memory and storage monitoring concepts. Its CSV history, alert records, plots and recommendations support evidence-based resource analysis and can be extended with a web dashboard, notification service or persistent database.
