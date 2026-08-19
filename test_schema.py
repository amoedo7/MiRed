#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
p = subprocess.run([sys.executable, str(HERE / 'mired.py'), '--no-probe', '--compact'], capture_output=True, text=True, check=True)
r = json.loads(p.stdout)
assert r['schema'] == 'desarrollamo.mired.v1'
assert isinstance(r['network'], dict)
assert r['privacy']['lan_scan_performed'] is False
assert r['privacy']['mac_addresses_collected'] is False
assert r['privacy']['wifi_credentials_collected'] is False
assert r['online']['enabled'] is False
assert r['summary']['probe_enabled'] is False
print('MiRed schema OK')
