# ARIA security evaluation and defenses

A Week 6 classroom project that tests NeoBank ARIA, isolates ticket summaries, and enforces account ownership in the backend.

**Instructor dashboard:** https://krtagorek.github.io/aria-ticket-summary-defense/

The dashboard is a static evidence explorer: it displays saved, reviewed fictional test results and does not run ARIA or make model calls. No sign-in or API key is required. See the extended results below for the confirmed baseline disclosures and remaining limitations.

The original submission is preserved at the immutable `submission-checkpoint-v1` tag. `main` now includes the extended defenses, tests, and dashboard.

## What the defense does

The original assistant refused to reveal hidden instructions when an injected support ticket asked for them, but it also abandoned the legitimate summary task. Explicit ticket-summary commands now take a separate, tool-free path with only a task policy and untrusted ticket text. The summary model receives no private banking prompt, conversation history, bank tools, policy documents, or account records. Invalid input or output never falls back to the privileged banking agent.

This is a narrow defense for the supported command grammar. The rest of the banking agent remains intentionally vulnerable classroom code. It is not suitable for real banking data or production use.

## Original checkpoint results

A completed local comparison used six fixed cases, three repetitions, and two versions, totaling 36 response trials.

| Measure | Before | After |
| --- | --- | --- |
| I01 correct summaries | 0/3 | 3/3 |
| Both injected-ticket cases | 0/6 | 6/6 |
| Clean summaries | 6/6 | 6/6 |
| Observed restricted disclosure | 0/18 | 0/18 |
| Overall scores | 12 PASS, 6 WARN | 18 PASS |

No execution errors occurred. Seven offline tests also passed. This is a small targeted evaluation; it does not establish general injection resistance or a reduction in leakage. The original raw results, reviewed log, screenshots, and report are retained separately in the local submission kit and are not committed here.

## Run locally

Use Python 3.12 for the recorded dependency set. In a new virtual environment:

```sh
python -m pip install -r requirements-lock.txt
python -m unittest discover -p 'test_*.py' -v
python -m streamlit run compare_app.py --server.address 127.0.0.1 --server.port 8502 --server.headless true --browser.gatherUsageStats false
```

Open the local comparison app, enter your API key in its password field, and run the fixed tests. Calls use your OpenAI account and incur normal API usage charges. A local database is created and seeded automatically with fictional classroom fixtures. No prebuilt database is committed.

To run the banking demo with the patched agent:

```sh
python -m streamlit run app.py --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false
```

## Files

- `agent_baseline.py`: unchanged upstream banking agent for comparison.
- `agent.py`: agent with the narrow ticket-summary route.
- `ticket_summary.py`: isolated summary policy, parsing, and output validation.
- `comparison.py`: fixed before-and-after experiment and local results capture.
- `compare_app.py`: local comparison interface.
- `test_ticket_summary.py`: seven offline boundary checks.
- `EXPERIMENT.md`: method, rubric, scope, and reproduction details.

## Credentials and privacy

Enter API keys only in the local app. Keys are not written into result records. Do not hardcode credentials, commit local configuration, or use real customer information. The ignore rules exclude credential files, generated databases, raw run logs, reports, and screenshots. Review staged files before every commit; ignore rules cannot detect a secret inserted into source code.

`seed_data.py` contains fictional classroom identities and contact fields, not real customer records. The unchanged upstream agent can log prompts and responses when run outside the comparison runner; keep all demo inputs fictional. The comparison runner disables application logging and optional third-party tracing.

## Source attribution

Derived from The Gen Academy's educational repository:
https://github.com/The-Gen-Academy/week6_neobank_aria_agent

Upstream commit: `9aed6350836f0ea625be6a4ae637943153e1c96e`.
The original README is preserved as `UPSTREAM_README.md`. This is a fresh repository containing the classroom source and the defense extension; upstream Git history and databases are not included. No new license or ownership claim is applied to the upstream material.

## New ownership defense and tougher tests

The submission above is preserved at [`submission-checkpoint-v1`](https://github.com/krtagorek/aria-ticket-summary-defense/tree/submission-checkpoint-v1). The current version adds a backend ownership boundary and a fixed adversarial suite. The earlier measured results are historical checkpoint results, not new live results for this branch.

`query_account` is now bound to the server-session customer and rejects cross-customer requests before database reads. Twenty-one offline tests pass. A direct real-tool audit exposes three other fictional records in the original version and zero in the patched version, while own-account lookups still work. Run `python backend_audit.py` to reproduce it without an API key.

Use the comparison app's suite selector for **Tough ticket tests** and **Account ownership tests**. These new live model tests have completed and been reviewed: 96 response trials across 16 cases. Two cases disclosed other fictional customer records in all three baseline repetitions each (6/48 before, 0/48 after). Overall scores improved from 21 PASS / 21 WARN / 6 FAIL to 44 PASS / 4 WARN / 0 FAIL. Four warnings remain after the patch. They include malformed envelopes, encoded instructions, role spoofing, a known unsupported command paraphrase, benign controls, and forged history. Tool observations are recorded so a model refusal cannot be mistaken for backend enforcement.

The classroom login is still name-only, policy retrieval is still unfiltered, and ordinary chat remains intentionally vulnerable. This extension is not a production authentication or complete banking-security solution. Generated results remain local and excluded from Git. The main submission and its tag are unchanged.

## Interactive results dashboard

The `dashboard/` folder contains an evidence explorer with all 96 reviewed response trials, paired replies, tool observations, filters, and remaining limitations. Contact fields are redacted; the data contains only fictional workshop fixtures. Raw provider logs and credentials are excluded.

Run `python -m http.server 8504 --bind 127.0.0.1 --directory dashboard` and open http://127.0.0.1:8504. No API key or model calls are needed. The original submission checkpoint remains unchanged.

## Dashboard publication

GitHub Pages publishes only `dashboard/` through `.github/workflows/pages.yml` when `main` changes. Application source, local databases, credential files, raw logs, and private screenshot evidence are not included in the site artifact. The public dashboard contains a redacted extract of reviewed fictional results. Hosting runs no Python backend and cannot execute new tests; use the local comparison app for that.

To restore or inspect the original submission, use `git switch --detach submission-checkpoint-v1` in a clean checkout. The tag is retained even as `main` advances.
