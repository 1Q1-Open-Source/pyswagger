Python 2 Removal — Tracking Log
================================

Purpose
--------
This file tracks the end-to-end removal of Python 2 compatibility from the repository, consolidation on Python 3.10+, and the associated refactors, documentation updates, and dependency cleanup.

Context and decisions
---------------------
- Target runtime: Python 3.10+ (confirmed).
- Legacy webapp2 client: removed; tests skipped with a module-level SkipTest to preserve path without running legacy code.
- PR strategy: staged (core+clients → primitives+scanner → spec/metaclass → tests → dependencies → docs).

High-level checklist
--------------------
Legend: [x] = done, [~] = in progress, [ ] = todo

Packaging and metadata
- [x] setup.py: add python_requires>=3.10; remove Py2 classifiers; add 3.10–3.12
- [ ] setup.py: drop `six` from install_requires (after code/tests stop importing it)
- [ ] requirements.txt: drop `six` (after code/tests stop importing it)

Codebase cleanup (src)
- [x] Remove webapp2 client (Python 2 only) — replaced with stub raising NotImplementedError
- [~] Remove `six` usage in core modules
  - [x] utils.py
  - [x] io.py
  - [x] getter.py
  - [x] resolve.py
  - [x] scan.py
  - [x] contrib/client/requests.py
  - [x] contrib/client/flask.py
  - [ ] contrib/client/tornado.py (also remove `from __future__ import absolute_import`)
- [ ] Remove `six` and Py2 shims from primitives
  - [x] primitives/_str.py
  - [ ] primitives/_uuid.py (replace six.string_types/binary_type; drop __future__)
  - [ ] primitives/_array.py, _byte.py, _model.py, _time.py, codec.py, render.py
- [ ] Remove `six` and Py2 metaclass helpers from spec and scanners
  - [ ] spec/base.py, spec/v1_2/objects.py, spec/v2_0/objects.py
  - [ ] scanner/*, scanner/v1_2/*, scanner/v2_0/* (if any `six` remains)
- [ ] Remove all `from __future__ import absolute_import` (any remaining occurrences)

Tests
- [x] Remove/skip webapp2 tests as legacy
- [ ] Remove `six` in tests: replace string/number/xrange helpers; adjust expectations to Py3 types

Documentation
- [x] README: update supported Python versions; remove webapp2 note; add contribution/test notes for Py3.10+
- [ ] PORTING_STEP_* docs: ensure consistency with Python 3-only and the cleanup status
- [ ] Step 7 docs: update installation to Git-based; add migration notes (headers list[str], HAL, UUID); verify links

Verification
- [ ] Run pytest and fix regressions
- [ ] Confirm optional deps treatment (werkzeug/flask, tornado, yaml, validate_email) in dev requirements/docs

Progress log
------------
2025-11-27 16:28 (local)
- Updated packaging to Python 3.10+; excluded legacy webapp2 client from packaging.
- Replaced legacy webapp2 client with a stub; skipped webapp2 tests at import.
- Began `six` removal across core: updated utils.py, io.py, getter.py, resolve.py, scan.py, requests and flask clients.
- Updated README to reflect Python 3.10+ and removed Python 2 references.
- Next up: finish primitives (`_uuid.py` et al.), spec/metaclass cleanups, tornado client, tests modernization, then drop `six` from dependencies and finalize docs.

How to use this tracking file
----------------------------
- Update the checklist as items are completed (convert [ ] → [x]).
- Add dated entries under Progress log for noteworthy milestones or decisions.
- Cross-link relevant PRs/issues when available.

References
----------
- PORTING_STEP_7.md — documentation updates and migration guidance plan
- README.md — user-facing support matrix and installation guidance
- setup.py, requirements.txt — packaging/dependency state
