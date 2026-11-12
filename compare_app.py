import json
from pathlib import Path
import streamlit as st
from comparison import execute, SUITES
st.set_page_config(page_title='ARIA before and after',layout='wide')
st.title('ARIA before and after')
st.write('Compare the original source with ticket isolation and backend account ownership checks. The original submission is preserved at submission-checkpoint-v1.')
st.info('Use only the fictional classroom data. Your key is sent to OpenAI for the tests; it is not included in the saved results. Model responses are saved locally for review.')
key=st.text_input('OpenAI API key',type='password',key='private_key')
repeats=st.radio('Repetitions per test and version',[1,3],index=1,horizontal=True)
suite=st.selectbox('Test suite',list(SUITES),index=1)
cases=SUITES[suite]
st.caption(f'{len(cases)*repeats*2} response trials. Each trial uses zero to two model requests. Calls use your API account and incur normal usage charges.')
with st.expander('View fixed test set'):
    for c in cases:
        st.write(c['id']+' — '+c['expectation']);st.code(c['prompt'],language=None,wrap_lines=True)
        if c.get('history'): st.json(c['history'])
# Results remain under this project when running locally or in the extracted kit.
result_key='results_'+suite
RESULTS=Path(__file__).resolve().parent/('comparison_results_'+suite.lower().replace(' ','_')+'.json')
if st.button('Run before and after',type='primary',disabled=not key):
    bar=st.progress(0); status=st.empty()
    def progress(n,total,row):
        bar.progress(n/total);status.write(f"Completed {n}/{total}: {row['id']} {row['variant']} repetition {row['repetition']}")
    with st.spinner('Running matching local tests'):
        st.session_state[result_key]=execute(key,repeats,progress,RESULTS,suite=suite)
    st.success('Run complete. Review the paired responses and save screenshots below.')
if result_key not in st.session_state and RESULTS.exists():
    st.session_state[result_key]=json.loads(RESULTS.read_text())
if result_key in st.session_state:
    results=st.session_state[result_key]
    st.download_button('Download raw results',json.dumps(results,indent=2),'aria_comparison_results.json','application/json')
    st.caption('Raw results are unscored until we review them. Errors must not be counted as passes. Capture both columns for I01 and its clean control.')
    for c in cases:
        st.subheader(c['id']+' — '+c['kind'].replace('_',' '))
        st.write('Expected: '+c['expectation'])
        st.code(c['prompt'],language=None,wrap_lines=True)
        for repetition in range(1,results['settings']['repetitions']+1):
            st.markdown(f'**Repetition {repetition}**')
            cols=st.columns(2)
            for col,variant in zip(cols,['before','after']):
                with col:
                    st.markdown('**'+variant.title()+'**')
                    rows=[r for r in results['records'] if r['id']==c['id'] and r['variant']==variant and r['repetition']==repetition]
                    if rows:
                        r=rows[0]
                        if r['error']:st.error('Execution error: '+r['error'])
                        st.write(r['response'] or 'No response recorded.')
                        if r.get('tool_observations'):
                            with st.expander('Observed tool calls and backend responses'):
                                st.json(r['tool_observations'])
                        st.caption(str(r['elapsed_seconds'])+' seconds • pending human review')
