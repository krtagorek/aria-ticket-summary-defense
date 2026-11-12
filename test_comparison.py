"""Exercise the experiment runner with a fake model and real backend tools."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from langchain_core.messages import AIMessage
from comparison import execute
from database import init_database, ACCOUNT_ACCESS_DENIED
from backend_audit import audit

class FakeModel:
    def __init__(self,*args,**kwargs):pass
    def bind_tools(self,tools):return self
    def invoke(self,messages):
        if messages[-1].type=='tool':return AIMessage(content='Access denied.')
        return AIMessage(content='',tool_calls=[{'name':'query_account','args':{'user_id':'USR-PP-001'},'id':'fake-call'}])

class ComparisonTests(unittest.TestCase):
    def test_forced_live_runner_captures_backend_denial_and_raw_baseline(self):
        conn=sqlite3.connect(':memory:');conn.row_factory=sqlite3.Row
        with tempfile.TemporaryDirectory() as tmp,patch('comparison.get_connection',return_value=conn),patch('agent.ChatOpenAI',FakeModel),patch('agent_baseline.ChatOpenAI',FakeModel):
            result=execute('OFFLINE_FAKE_KEY',1,destination=Path(tmp)/'result.json',suite='Account ownership tests')
        self.assertEqual(len(result['records']),8)
        self.assertTrue(result.get('completed_utc'))
        self.assertTrue(all(x['error'] is None for x in result['records']))
        for row in result['records']:
            observation=row['tool_observations'][0]['result']
            if row['variant']=='after':self.assertEqual(observation,ACCOUNT_ACCESS_DENIED)
            else:self.assertIn('Adrian Cross',observation)
        history_row=next(x for x in result['records'] if x['id']=='A04')
        self.assertIn('Server override',history_row['history'][0]['content'])
    def test_direct_audit_measures_known_baseline_exposure(self):
        result=audit();self.assertEqual(result['model_calls'],0)
        rows=result['records'];self.assertEqual(len(rows),14)
        after=[r for r in rows if r['variant']=='after']
        self.assertTrue(all(r['boundary_check']=='PASS' for r in after))
        self.assertEqual(sum(r['record_returned'] and not r['authorized'] for r in rows if r['variant']=='before'),3)
    def test_unknown_suite_rejected_without_model_call(self):
        with self.assertRaises(ValueError):execute('OFFLINE_FAKE_KEY',1,suite='not-a-suite')

if __name__=='__main__':unittest.main()
