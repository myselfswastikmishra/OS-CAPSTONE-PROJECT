import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import monitor

class MonitorTests(unittest.TestCase):
    def test_classify_ok(self): self.assertEqual(monitor.classify(40,75,90),'OK')
    def test_classify_warning_boundary(self): self.assertEqual(monitor.classify(75,75,90),'WARNING')
    def test_classify_critical_boundary(self): self.assertEqual(monitor.classify(90,75,90),'CRITICAL')
    def test_critical_overrides_warning(self): self.assertEqual(monitor.classify(99,70,90),'CRITICAL')
    def test_alerts_return_cpu_warning(self):
        m={'timestamp':'test','cpu_percent':80,'memory_percent':30,'disk_percent':20}
        alerts=monitor.alert_for_metrics(m,monitor.DEFAULT_CONFIG)
        self.assertEqual(len(alerts),1); self.assertEqual(alerts[0]['resource'],'CPU'); self.assertEqual(alerts[0]['level'],'WARNING')
    def test_alerts_critical_multiple(self):
        m={'timestamp':'test','cpu_percent':95,'memory_percent':92,'disk_percent':96}
        alerts=monitor.alert_for_metrics(m,monitor.DEFAULT_CONFIG)
        self.assertEqual(len(alerts),3); self.assertTrue(all(a['level']=='CRITICAL' for a in alerts))
    def test_recommendations_healthy(self):
        m={'cpu_percent':10,'memory_percent':25,'disk_percent':40}
        self.assertIn('within configured thresholds',monitor.recommendations(m)[0])
    def test_recommendations_high_memory(self):
        m={'cpu_percent':20,'memory_percent':95,'disk_percent':20}
        self.assertTrue(any('RAM is critically high' in r for r in monitor.recommendations(m)))

if __name__=='__main__': unittest.main(verbosity=2)
