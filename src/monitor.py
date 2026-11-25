#!/usr/bin/env python3
"""OS Resource Monitoring & Alert System - integrated monitoring capstone."""
from __future__ import annotations
import argparse, csv, json, logging, os, platform, shutil, subprocess, sys, time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'output'
LOGS = ROOT / 'logs'
CONFIG = DATA / 'config.json'
METRICS = OUT / 'metrics.csv'
ALERTS = OUT / 'alerts.csv'
PROCESSES = OUT / 'processes.csv'

for folder in (DATA, OUT, LOGS): folder.mkdir(parents=True, exist_ok=True)
logging.basicConfig(filename=LOGS/'activity.log', level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

DEFAULT_CONFIG = {'interval_seconds': 2, 'cpu_warning': 75, 'cpu_critical': 90, 'memory_warning': 75, 'memory_critical': 90, 'disk_warning': 80, 'disk_critical': 95, 'disk_path': None, 'top_processes': 10}

def load_config():
    if not CONFIG.exists(): CONFIG.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
    try:
        cfg = json.loads(CONFIG.read_text())
        merged = DEFAULT_CONFIG.copy(); merged.update(cfg)
        return merged
    except (json.JSONDecodeError, OSError) as exc:
        logging.exception('Config read failed; defaults loaded: %s', exc)
        return DEFAULT_CONFIG.copy()


def get_psutil():
    try: import psutil
    except ImportError:
        print('Missing dependency: psutil. Install with: python -m pip install psutil')
        raise SystemExit(1)
    return psutil


def timestamp(): return datetime.now().astimezone().isoformat(timespec='seconds')

def classify(value, warning, critical):
    if value >= critical: return 'CRITICAL'
    if value >= warning: return 'WARNING'
    return 'OK'

def collect_metrics():
    ps = get_psutil(); cfg = load_config()
    cpu = ps.cpu_percent(interval=0.25)
    vm = ps.virtual_memory()
    disk_path = cfg.get('disk_path') or (os.environ.get('SystemDrive', 'C:') + '\\' if os.name == 'nt' else '/')
    try: du = ps.disk_usage(disk_path)
    except (OSError, ValueError): du = ps.disk_usage('/')
    net = ps.net_io_counters()
    return {'timestamp': timestamp(), 'hostname': platform.node(), 'platform': platform.platform(), 'cpu_percent': round(cpu, 2), 'memory_total_mb': round(vm.total/1024**2, 2), 'memory_used_mb': round(vm.used/1024**2, 2), 'memory_available_mb': round(vm.available/1024**2, 2), 'memory_percent': round(vm.percent, 2), 'disk_path': disk_path, 'disk_total_gb': round(du.total/1024**3, 2), 'disk_used_gb': round(du.used/1024**3, 2), 'disk_free_gb': round(du.free/1024**3, 2), 'disk_percent': round(du.percent, 2), 'process_count': len(ps.pids()), 'bytes_sent': net.bytes_sent, 'bytes_recv': net.bytes_recv}

def append_csv(path, row):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if f.tell() == 0: writer.writeheader()
        writer.writerow(row)

def alert_for_metrics(m, cfg=None):
    cfg = cfg or load_config(); alerts=[]
    for resource, val, warn, crit in [('CPU', m['cpu_percent'], cfg['cpu_warning'], cfg['cpu_critical']), ('MEMORY', m['memory_percent'], cfg['memory_warning'], cfg['memory_critical']), ('DISK', m['disk_percent'], cfg['disk_warning'], cfg['disk_critical'])]:
        level=classify(val, warn, crit)
        if level != 'OK': alerts.append({'timestamp':m['timestamp'], 'resource':resource, 'level':level, 'value_percent':val, 'message':f'{resource} utilization {val:.1f}% is {level.lower()} (warning {warn}%, critical {crit}%)'})
    return alerts

def record_sample():
    m=collect_metrics(); append_csv(METRICS, m)
    cfg=load_config()
    for alert in alert_for_metrics(m, cfg):
        append_csv(ALERTS, alert); logging.warning(alert['message']); print(f"\033[91m[{alert['level']}] {alert['message']}\033[0m")
    logging.info('Sample recorded')
    return m

def get_processes(limit=None):
    ps=get_psutil(); cfg=load_config(); limit=limit or cfg['top_processes']; rows=[]
    for p in ps.process_iter(['pid','name','username','memory_info']):
        try:
            p.cpu_percent(None)
        except (ps.NoSuchProcess, ps.AccessDenied): pass
    time.sleep(0.15)
    for p in ps.process_iter(['pid','name','username','memory_info']):
        try:
            info=p.info; mem=info.get('memory_info'); rows.append({'pid':info['pid'],'name':info.get('name') or '', 'username':info.get('username') or '', 'cpu_percent':round(p.cpu_percent(None),2), 'memory_mb':round(mem.rss/1024**2,2) if mem else 0})
        except (ps.NoSuchProcess, ps.AccessDenied, ps.ZombieProcess): continue
    rows.sort(key=lambda x:x['cpu_percent'], reverse=True)
    return rows[:limit], rows

def print_dashboard(m):
    print('\n'+'='*66); print(' OS RESOURCE MONITORING & ALERT SYSTEM '.center(66)); print('='*66)
    print(f"Timestamp : {m['timestamp']} | Host: {m['hostname']}")
    print(f"CPU      : {m['cpu_percent']:6.1f}%")
    print(f"RAM      : {m['memory_percent']:6.1f}% | {m['memory_used_mb']:,.0f} MB used / {m['memory_total_mb']:,.0f} MB")
    print(f"Disk     : {m['disk_percent']:6.1f}% | {m['disk_used_gb']:,.2f} GB used / {m['disk_total_gb']:,.2f} GB")
    print(f"Processes : {m['process_count']}")
    print('='*66)

def live_monitor():
    cfg=load_config(); interval=max(1, int(cfg.get('interval_seconds',2)))
    print(f'Live monitoring started (sampling every {interval}s). Ctrl+C to stop.')
    try:
        while True:
            m=record_sample(); print_dashboard(m); time.sleep(interval)
    except KeyboardInterrupt: print('\nMonitoring stopped by user. Samples saved to output/metrics.csv')

def process_view():
    top, all_rows=get_processes()
    print('\nTOP PROCESSES BY CPU\nPID      CPU%    RAM(MB)   PROCESS')
    for r in top: print(f"{r['pid']:<8} {r['cpu_percent']:>6.1f} {r['memory_mb']:>9.1f}   {r['name'][:42]}")
    for r in all_rows: append_csv(PROCESSES, {'timestamp':timestamp(), **r})
    print(f'\nProcess snapshot saved ({len(all_rows)} processes) to {PROCESSES.name}')

def show_alerts():
    if not ALERTS.exists(): print('No alerts recorded yet.'); return
    with ALERTS.open(encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    print('\nALERT HISTORY (latest 20)')
    for r in rows[-20:]: print(f"{r['timestamp']} | {r['level']:<8} | {r['resource']:<8} | {r['message']}")

def recommendations(m):
    rec=[]
    if m['cpu_percent']>=90: rec.append('CPU is critically high: inspect top CPU processes, reduce background work, or investigate runaway tasks.')
    elif m['cpu_percent']>=75: rec.append('CPU is elevated: review CPU-heavy applications and scheduled tasks.')
    if m['memory_percent']>=90: rec.append('RAM is critically high: close memory-heavy applications or consider additional RAM.')
    elif m['memory_percent']>=75: rec.append('RAM is elevated: inspect top memory processes and unnecessary applications.')
    if m['disk_percent']>=95: rec.append('Disk is critically full: remove/archivе large files and check temporary data.')
    elif m['disk_percent']>=80: rec.append('Disk usage is high: review storage and consider cleanup.')
    if not rec: rec.append('Resource levels are within configured thresholds. Continue monitoring for trends.')
    return rec

def health_analysis():
    m=record_sample(); print_dashboard(m); print('\nSYSTEM HEALTH ANALYSIS & RECOMMENDATIONS')
    for r in recommendations(m): print(' • '+r)

def generate_report():
    m=record_sample(); print_dashboard(m)
    lines = [
        'OS RESOURCE MONITORING REPORT', f"Generated: {m['timestamp']}", f"Host: {m['hostname']}", '',
        'CURRENT METRICS', f"CPU: {m['cpu_percent']}%", f"RAM: {m['memory_percent']}% ({m['memory_used_mb']} MB used)",
        f"Disk: {m['disk_percent']}% ({m['disk_used_gb']} GB used)", f"Processes: {m['process_count']}", '', 'RECOMMENDATIONS'
    ] + ['- ' + r for r in recommendations(m)]
    if METRICS.exists():
        with METRICS.open(encoding='utf-8') as f: history = list(csv.DictReader(f))
        lines += ['', f'HISTORY: {len(history)} samples recorded']
        if history:
            for key in ('cpu_percent', 'memory_percent', 'disk_percent'):
                vals = [float(x[key]) for x in history if x.get(key)]
                if vals: lines.append(f'{key}: min={min(vals):.2f}% max={max(vals):.2f}% mean={sum(vals)/len(vals):.2f}%')
    path = OUT/'system_report.txt'; path.write_text('\n'.join(lines), encoding='utf-8'); print(f'\nReport saved: {path}')

def generate_graphs():
    if not METRICS.exists(): print('No metric history yet. Start monitoring first.'); return
    try: import matplotlib.pyplot as plt
    except ImportError: print('Matplotlib missing. Install: python -m pip install matplotlib'); return
    with METRICS.open(encoding='utf-8') as f: rows=list(csv.DictReader(f))
    if len(rows)<2: print('Need at least 2 metric samples to graph.'); return
    labels=[r['timestamp'].split('T')[-1] for r in rows]
    for key,title in [('cpu_percent','CPU Utilization'),('memory_percent','Memory Utilization'),('disk_percent','Disk Utilization')]:
        vals=[float(r[key]) for r in rows]
        plt.figure(figsize=(10,4)); plt.plot(range(len(vals)),vals,marker='.',linewidth=1.5); plt.title(title+' Over Time'); plt.xlabel('Sample'); plt.ylabel('Usage (%)'); plt.ylim(0,100); plt.grid(True,alpha=.3); plt.tight_layout(); p=OUT/(key.replace('_percent','')+'_history.png'); plt.savefig(p,dpi=160); plt.close(); print('Graph saved:',p)
    plt.figure(figsize=(10,4)); plt.plot(range(len(rows)),[float(r['cpu_percent']) for r in rows],label='CPU'); plt.plot(range(len(rows)),[float(r['memory_percent']) for r in rows],label='Memory'); plt.plot(range(len(rows)),[float(r['disk_percent']) for r in rows],label='Disk'); plt.title('Resource Utilization Comparison'); plt.xlabel('Sample'); plt.ylabel('Usage (%)'); plt.ylim(0,100); plt.grid(True,alpha=.3); plt.legend(); plt.tight_layout(); p=OUT/'resource_comparison.png'; plt.savefig(p,dpi=160); plt.close(); print('Graph saved:',p)

def configure_thresholds():
    cfg=load_config(); print('Thresholds are percentages. Enter blank to keep current.')
    for resource in ('cpu','memory','disk'):
        for level in ('warning','critical'):
            key=f'{resource}_{level}'; current=cfg[key]
            try: value=input(f'{key} [{current}]: ').strip()
            except EOFError: value=''
            if value:
                try: n=float(value)
                except ValueError: print('Invalid number, unchanged.'); continue
                if not 0<=n<=100: print('Value must be 0-100, unchanged.'); continue
                cfg[key]=n
    for resource in ('cpu','memory','disk'):
        if cfg[f'{resource}_warning']>=cfg[f'{resource}_critical']:
            print(f'Warning threshold must be lower than critical for {resource}; retaining previous configuration for this resource.')
            cfg[f'{resource}_warning']=DEFAULT_CONFIG[f'{resource}_warning']; cfg[f'{resource}_critical']=DEFAULT_CONFIG[f'{resource}_critical']
    CONFIG.write_text(json.dumps(cfg,indent=2)); print('Configuration saved to data/config.json')

def export_data():
    print('Data files:');
    for p in (METRICS, ALERTS, PROCESSES): print(f'  {p}: {"exists" if p.exists() else "not created yet"}')
    print('All data is stored as CSV in the output directory.')

def menu():
    while True:
        print('\n'+'='*60+'\n OS RESOURCE MONITORING & ALERT SYSTEM\n'+'='*60)
        print('1. Live System Dashboard\n2. Collect One Metric Snapshot\n3. Process Monitoring\n4. Top CPU Processes\n5. Top Memory Processes\n6. Alert History\n7. Generate Performance Report\n8. Generate Graphs\n9. System Health Analysis\n10. Configure Alert Thresholds\n11. Show Data File Locations\n0. Exit')
        try: choice=input('Select option: ').strip()
        except EOFError: break
        try:
            if choice=='1': live_monitor()
            elif choice=='2': print_dashboard(record_sample())
            elif choice=='3': process_view()
            elif choice in ('4','5'):
                _,rows=get_processes(limit=100); rows.sort(key=lambda r:r['cpu_percent' if choice=='4' else 'memory_mb'],reverse=True); print('\nPID       CPU%    RAM(MB)  NAME'); [print(f"{r['pid']:<9}{r['cpu_percent']:>6.1f}{r['memory_mb']:>10.1f}  {r['name'][:40]}") for r in rows[:10]]
            elif choice=='6': show_alerts()
            elif choice=='7': generate_report()
            elif choice=='8': generate_graphs()
            elif choice=='9': health_analysis()
            elif choice=='10': configure_thresholds()
            elif choice=='11': export_data()
            elif choice=='0': print('Exiting.'); break
            else: print('Invalid menu option. Choose 0-11.')
        except (OSError, RuntimeError, ValueError) as e: print('Operation failed:',e); logging.exception('Menu operation failed')

def main():
    parser=argparse.ArgumentParser(description='OS Resource Monitoring & Alert System')
    parser.add_argument('--once',action='store_true',help='Collect one sample and print dashboard')
    parser.add_argument('--monitor',action='store_true',help='Start continuous monitoring')
    parser.add_argument('--report',action='store_true',help='Generate report')
    parser.add_argument('--graphs',action='store_true',help='Generate graphs from existing history')
    args=parser.parse_args()
    if args.once: print_dashboard(record_sample())
    elif args.monitor: live_monitor()
    elif args.report: generate_report()
    elif args.graphs: generate_graphs()
    else: menu()
if __name__=='__main__': main()
