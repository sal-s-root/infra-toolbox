import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent

class Toolbox(unittest.TestCase):
    def test_all_documented_fixtures(self):
        for row in json.loads((ROOT/'catalog.json').read_text()):
            with self.subTest(tool=row['name']):
                folder=ROOT/'checks'/row['name']
                spec=importlib.util.spec_from_file_location('check_'+row['name'].replace('-','_'),folder/'tool.py')
                module=importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                data=json.loads((folder/'examples/input.json').read_text())
                expected=json.loads((folder/'examples/expected.json').read_text())
                self.assertEqual(module.evaluate(data),expected)
    def test_area_listing(self):
        result=subprocess.run([sys.executable,str(ROOT/'toolbox.py'),'list','--area','networking'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('cidr-overlap-checker',result.stdout)
        self.assertNotIn('disk-capacity-planner',result.stdout)
    def test_command_invocation(self):
        result=subprocess.run([sys.executable,str(ROOT/'toolbox.py'),'run','disk-capacity-planner',str(ROOT/'checks/disk-capacity-planner/examples/input.json')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['used_percent'],65)
    def test_unknown_tool_is_rejected(self):
        result=subprocess.run([sys.executable,str(ROOT/'toolbox.py'),'run','../other'],capture_output=True,text=True)
        self.assertEqual(result.returncode,2)

if __name__=='__main__':
    unittest.main()
