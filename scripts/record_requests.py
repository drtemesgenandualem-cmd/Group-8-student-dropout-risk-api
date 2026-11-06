"""Record actual HTTP responses from a running service; run from prediction_api/."""
import argparse
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--base-url', default='http://127.0.0.1:8000')
args = parser.parse_args()
good = json.loads((ROOT / 'examples/valid_student.json').read_text())
missing = dict(good)
del missing['Age at enrollment']
cases = {
    'missing_field': missing,
    'wrong_type': {**good, 'Age at enrollment': 'young'},
    'out_of_range': {**good, 'Age at enrollment': 900},
    'invalid_category': {**good, 'Course': 999},
}
records = []
with httpx.Client(base_url=args.base_url, timeout=30) as client:
    health = client.get('/health')
    health.raise_for_status()
    (ROOT / 'evidence/health_response.json').write_text(json.dumps(health.json(), indent=2)+'\n')
    valid = client.post('/predict', json=good)
    valid.raise_for_status()
    (ROOT / 'evidence/successful_prediction.json').write_text(json.dumps(valid.json(), indent=2)+'\n')
    for name, payload in cases.items():
        response = client.post('/predict', json=payload)
        assert response.status_code == 422, (name, response.text)
        records.append({'test': name, 'request': payload, 'status_code': response.status_code, 'response': response.json()})
    spec = client.get('/openapi.json')
    spec.raise_for_status()
    (ROOT / 'evidence/openapi.json').write_text(json.dumps(spec.json(), indent=2)+'\n')
log = {'recorded_at': datetime.now(ZoneInfo('Africa/Addis_Ababa')).isoformat(), 'base_url': args.base_url, 'requests': records}
(ROOT / 'evidence/invalid_input_log.json').write_text(json.dumps(log, indent=2)+'\n')
lines = ['# Invalid-input log', '', f"Recorded: {log['recorded_at']} (Africa/Addis_Ababa). Actual requests to `{args.base_url}/predict`.", '', '| Test | Change to valid request | HTTP status | Actual message |', '|---|---|---|---|']
changes = ['Remove `Age at enrollment`', '`Age at enrollment`: `"young"`', '`Age at enrollment`: `900`', '`Course`: `999`']
for record, change in zip(records, changes):
    message = '; '.join(error['msg'] for error in record['response']['detail'])
    lines.append(f"| {record['test']} | {change} | {record['status_code']} | {message} |")
lines += ['', 'Full request bodies and responses: [invalid_input_log.json](invalid_input_log.json).', 'Each request starts with [valid_student.json](../examples/valid_student.json) and applies the change shown above.', '']
(ROOT / 'evidence/invalid_input_log.md').write_text('\n'.join(lines))
print(json.dumps(valid.json(), indent=2))
print(f'Recorded {len(records)} invalid requests, health, successful prediction and OpenAPI.')
