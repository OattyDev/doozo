#!/usr/bin/env python3
"""Summarize immutable first-attempt rows and separate trace-audit sidecars."""
import argparse
import json
import statistics
from pathlib import Path


def summarize(run):
    rows = [json.loads(line) for line in (run / 'results.jsonl').read_text().splitlines()]
    audits = {}
    for case in {row['case'] for row in rows}:
        base = run / 'audits' / (case + '.json')
        adjudicated = run / 'audits' / (case + '-adjudication.json')
        path = adjudicated if adjudicated.exists() else base
        if path.exists():
            for audit in json.loads(path.read_text()):
                key = str(Path(audit['source_result']).resolve())
                if key in audits: raise ValueError('Duplicate audit for ' + key)
                audits[key] = audit
    seen = set()
    arms = {arm: [] for arm in ('plain','v01','v02')}
    for row in rows:
        key = (row['case'], row['repeat'], row['arm'])
        if key in seen: raise ValueError('Repeated attempt cannot replace first pass: ' + str(key))
        seen.add(key)
        result_path = str((Path(row['artifacts']['final']).parent / 'result.json').resolve())
        row = {**row, 'audit': audits.get(result_path)}
        arms.setdefault(row['arm'], []).append(row)
    summary = {}
    for arm, records in arms.items():
        complete = bool(records) and all(row['audit'] is not None for row in records)
        token_complete = bool(records) and all(row.get('total_token_usage') is not None for row in records)
        summary[arm] = {
            'attempts': len(records),
            'audited': sum(row['audit'] is not None for row in records),
            'first_pass_successes': sum(row['audit'].get('first_pass_correct') is True for row in records if row['audit']),
            'deterministic_failures': sum(row['status'] != 'deterministic_pass' for row in records),
            'tokens_all_attempts': sum(row['total_token_usage'] for row in records) if token_complete else None,
            'seconds_all_attempts': sum(row['elapsed_seconds'] for row in records),
            'median_tokens': statistics.median(row['total_token_usage'] for row in records) if token_complete else None,
            'median_seconds': statistics.median(row['elapsed_seconds'] for row in records) if records else None,
            'worker_count': sum(max(0,len(row.get('session_usage',{}).get('actors',[]))-1) for row in records),
            'internal_retries': sum(row['audit']['internal_retries'] for row in records) if complete else None,
            'human_interventions': sum(row['audit']['human_interventions'] for row in records) if complete else None,
            'human_requests': sum(row['audit']['human_requests'] for row in records) if complete else None,
            'unnecessary_executions': sum(len(row['audit']['unnecessary_executions']) for row in records) if complete else None,
            'test_executions': sum(row['audit']['test_execution_count'] for row in records) if complete else None,
            'regressions': sum(len(row['audit']['regressions']) for row in records) if complete else None,
            'missed_requirements': sum(len(row['audit']['missed_requirements']) for row in records) if complete else None,
        }
    pairs = []
    lookup = {(row['case'],row['repeat'],row['arm']):row for records in arms.values() for row in records}
    for candidate in arms['v02']:
        baseline = lookup.get((candidate['case'],candidate['repeat'],'v01'))
        if not baseline: continue
        if not all(row.get('audit') and row['audit'].get('first_pass_correct') is True and row['audit'].get('measurement_valid') is True for row in (candidate,baseline)): continue
        tokens = candidate.get('total_token_usage'); old_tokens = baseline.get('total_token_usage')
        pairs.append({'case':candidate['case'],'repeat':candidate['repeat'], 'token_ratio':tokens/old_tokens if tokens is not None and old_tokens else None,'time_ratio':candidate['elapsed_seconds']/baseline['elapsed_seconds']})
    return {'run':str(run),'arms':summary,'mutually_correct_pairs':pairs,'paired_median_token_ratio':statistics.median(p['token_ratio'] for p in pairs) if pairs and all(p['token_ratio'] is not None for p in pairs) else None,'paired_median_time_ratio':statistics.median(p['time_ratio'] for p in pairs) if pairs else None,'note':'Pending audits, missing usage, and unrun attempts prevent acceptance. Diagnostic and invalidated runs must be reported separately.'}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path)
    print(json.dumps(summarize(parser.parse_args().run),indent=2))
