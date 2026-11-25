# Assignment phase mapping

| Phase | Deliverables in this project | Evidence |
|---|---|---|
| 1. System Design and Planning | Monitoring architecture, collector/storage/alert/report modules, configuration and workflow | README, report, architecture diagram in submission |
| 2. Core Resource Modules | CPU, memory, disk, process monitoring, Python implementation and Bash launcher | source code, live dashboard, CSV snapshots |
| 3. Analysis and Comparison | Historical resource trends, min/max/mean summaries, graphs and recommendations | PNG graphs, report, metrics CSV |
| 4. Testing and Reliability | input validation, exception handling, permission-aware process iteration, 8 unit tests, logging | test output, logs, test cases |
| 5. Documentation and Demonstration | execution guide, report, sample config, launchers and output folder | README, report, demonstration trace/screenshots |


## Demonstration sequence
1. Launch application.
2. Collect one snapshot and show CPU/RAM/disk/process count.
3. Start live monitoring and let it collect multiple samples.
4. Demonstrate top processes.
5. Show alert history (if thresholds crossed) or explain configurable thresholds.
6. Generate performance report.
7. Generate graphs.
8. Run automated tests.
