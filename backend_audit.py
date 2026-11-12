"""Repeatable direct-tool audit using only in-memory fictional fixtures."""
import argparse
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import agent
import agent_baseline
from database import init_database, ACCOUNT_ACCESS_DENIED

TARGETS=[('own','USR-0042',True),('own_whitespace',' USR-0042 ',True),
         ('other_premier','USR-PP-001',False),('other_standard','USR-0007',False),
         ('other_staff','USR-STAFF-01',False),('unknown','USR-NOT-REAL',False),
         ('sql_payload',"USR-0042' OR 1=1 --",False)]

def audit():
    conn=sqlite3.connect(':memory:');conn.row_factory=sqlite3.Row;init_database(conn)
    rows=[];previous=logging.root.manager.disable;logging.disable(logging.CRITICAL)
    try:
        for variant,tools in [('before',agent_baseline.build_tools(conn)),('after',agent.build_tools(conn,'USR-0042'))]:
            lookup={t.name:t for t in tools}['query_account']
            for ident,target,own in TARGETS:
                response=lookup.invoke({'user_id':target})
                record='Account Details for ' in response
                denied=response==ACCOUNT_ACCESS_DENIED
                rows.append({'variant':variant,'case':ident,'target':target,'authorized':own,
                             'record_returned':record,'explicit_denial':denied,
                             'boundary_check':'PASS' if (record if own else denied) else 'FAIL'})
    finally:
        conn.close();logging.disable(previous)
    return {'kind':'direct_tool_audit','completed_utc':datetime.now(timezone.utc).isoformat(),
            'fixtures':'In-memory classroom data only','model_calls':0,'records':rows}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path)
    args=parser.parse_args();result=audit();text=json.dumps(result,indent=2)
    if args.out:args.out.write_text(text)
    print(text)
