import subprocess
import tempfile
import unittest
from pathlib import Path

from astra_benchmark import init_repo
from astra_tasks import CASE_BY_ID, protected_tests


class FrozenGraderTests(unittest.TestCase):
    def test_document_evidence_filename_is_not_a_hidden_requirement(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);case=CASE_BY_ID['doc-correction'];case.prepare(root);baseline=init_repo(root)
            doc=root/'docs/guide.md';doc.write_text(doc.read_text().replace('stop the import.', 'are skipped.'))
            (root/'evidence').mkdir();(root/'evidence/check.txt').write_text('Inspected corrected document.\n')
            (root/'doc-correction-evidence.txt').write_text('Inspected corrected document.\n')
            self.assertTrue(all(case.grade(root,baseline,'').values()))
            subprocess.run(['git','add','-A'],cwd=root,check=True,capture_output=True)
            subprocess.run(['git','commit','-qm','document and evidence'],cwd=root,check=True,capture_output=True)
            self.assertTrue(all(case.grade(root,baseline,'').values()))
            (root/'.gitignore').write_text('unrequested change to supplied file')
            self.assertFalse(case.grade(root,baseline,'')['supplied_files_preserved'])

    def test_original_failures_and_valid_outcomes(self):
        fixes = {
            'doc-correction': {'docs/guide.md': '# Importing\n\nImports that duplicate an existing record are skipped.\n\n## Limits\n\nFiles contain at most 100 rows.\n'},
            'whitespace-slug': {'slug.py': "def slug(value):\n return '-'.join(value.lower().split())\n"},
            'bounded-stdlib-feature': {'retry.py': 'def retry_delays(count):\n return [min(2**i,60) for i in range(count)]\n'},
            'multi-module-feature': {'catalog.py': "ITEMS=[{'id':1,'name':'Bolt'},{'id':2,'name':'Nut'}]\ndef find(query):\n return [x for x in ITEMS if query.strip().lower() in x['name'].lower()]\n", 'formatting.py': "def render(items):\n return '\\n'.join(str(i)+'. '+x['name'] for i,x in enumerate(items,1))\n"},
            'financial-rounding': {'money.py': 'def split_cents(total, people):\n if total<0 or people<=0: raise ValueError()\n q,r=divmod(total,people)\n return [q+int(i<r) for i in range(people)]\n'},
            'dirty-resume-stale-evidence': {'service.py': "def state():\n return 'ready'\n"},
        }
        for name, files in fixes.items():
            with self.subTest(case=name), tempfile.TemporaryDirectory() as temp:
                root=Path(temp); case=CASE_BY_ID[name];case.prepare(root);baseline=init_repo(root)
                if name=='dirty-resume-stale-evidence': (root/'notes.txt').write_text('user-local change\n')
                self.assertFalse(all(case.grade(root,baseline,'').values()))
                for path,content in files.items(): (root/path).write_text(content)
                if (root/'tests').exists(): (root/'tests/test_new.py').write_text('import unittest\nclass Added(unittest.TestCase):\n def test_new(self): self.assertTrue(True)\n')
                self.assertTrue(all(case.grade(root,baseline,'').values()))
                subprocess.run(['git','add','-A'],cwd=root,check=True,capture_output=True)
                subprocess.run(['git','commit','-qm','agent commit'],cwd=root,check=True,capture_output=True)
                self.assertTrue(all(case.grade(root,baseline,'').values()), 'committing must not hide changes')

    def test_cannot_hide_weakened_supplied_tests(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);CASE_BY_ID['whitespace-slug'].prepare(root);baseline=init_repo(root)
            (root/'tests/test_slug.py').write_text('')
            subprocess.run(['git','add','-A'],cwd=root,check=True,capture_output=True)
            subprocess.run(['git','commit','-qm','weaken tests'],cwd=root,check=True,capture_output=True)
            self.assertFalse(protected_tests(root,baseline))


if __name__=='__main__': unittest.main()
