import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('astra_summary', Path(__file__).parent/'astra/summarize.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class SummaryIntegrityTests(unittest.TestCase):
    def test_failed_run_stays_failed_and_missing_usage_stays_unknown(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'audits').mkdir()
            row={'case':'example','repeat':1,'arm':'v01','status':'deterministic_failure','artifacts':{'final':str(root/'case/final.txt')},'total_token_usage':None,'elapsed_seconds':600}
            (root/'results.jsonl').write_text(json.dumps(row)+'\n')
            audit={'source_result':str(root/'case/result.json'),'first_pass_correct':True,'measurement_valid':False,'internal_retries':0,'human_interventions':0,'human_requests':0,'unnecessary_executions':[],'test_execution_count':0,'regressions':[],'missed_requirements':[]}
            (root/'audits/example.json').write_text(json.dumps([audit]))
            summary=module.summarize(root)
            self.assertEqual(summary['arms']['v01']['first_pass_successes'],0)
            self.assertIsNone(summary['arms']['v01']['tokens_all_attempts'])
            later={**row,'status':'deterministic_pass','total_token_usage':100}
            with (root/'results.jsonl').open('a') as stream:stream.write(json.dumps(later)+'\n')
            with self.assertRaisesRegex(ValueError,'cannot replace first pass'):module.summarize(root)


if __name__=='__main__':unittest.main()
