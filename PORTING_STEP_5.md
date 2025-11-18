# Step 5 — CI and dependency refresh (GitHub Actions + requirements)

Date: 2025-11-18 13:29 (local)

This document captures only the fifth step from the initial porting plan: introduce/modernize continuous integration using GitHub Actions and refresh dependency pins so the project is reliably testable on supported Python versions (3.8–3.12). No runtime behavior is changed in this step.

## Objectives
- Add/modernize CI workflows (GitHub Actions) to run tests on Python 3.8, 3.10, and 3.12, with caching to keep runs fast.
- Optionally keep existing Travis/AppVeyor for a short transition window; GitHub Actions becomes the primary CI.
- Refresh dependency pins minimally to ensure install/test succeed across the matrix and to address known vulnerabilities (e.g., PyYAML safety, modern Flask/Werkzeug compatibility for tests).
- Update documentation badges and changelog to reflect CI changes.

## Scope
- In scope: CI workflow YAMLs under .github/workflows/ and conservative updates to requirements.txt / requirements-dev.txt.
- Out of scope: feature code, renderer defaults, codecs, client behavior, or release publishing (publishing can be added later).

## A) GitHub Actions workflows

1) Test matrix workflow
- File: .github/workflows/python-package.yml (name: Python package)
- Strategy:
  - runs-on: ubuntu-latest
  - Matrix over python-version: ["3.8", "3.10", "3.12"]
- Steps:
  - actions/checkout@v4
  - actions/setup-python@v5 with cache: pip
  - Install test dependencies: pip install -r requirements-dev.txt
  - Run tests: python -m pytest -s -v --cov=pyswagger --cov-config=.coveragerc pyswagger/tests
- Artifacts: optionally upload coverage XML for external services (defer if not used).

2) Lint workflow (optional but recommended in the same step if trivial)
- File: .github/workflows/lint.yml
- Tools: flake8 and/or pylint (matching any existing config if present). Keep thresholds lenient initially to avoid large refactors.

3) Windows/macOS coverage (optional)
- If builds are pure-Python, Linux may be sufficient. Add windows-latest and/or macos-latest later if issues arise.

4) Transition from Travis/AppVeyor
- Keep legacy badges/config for one iteration if they are still active.
- Prefer GitHub Actions badges; update README once Actions are green.

### Sources to reuse
- EngMahmoudTaha/develop: adds a `.github/workflows/pylint.yml` workflow which can inform our lint configuration.
- manatlan/develop: provides Python package workflows (test/publish); adapt the testing portions and omit publish steps since we distribute via Git.

## B) Dependency refresh (minimal, compatibility-focused)

1) Goals
- Ensure compatibility on Python 3.12 across the test matrix.
- Address security concerns (PyYAML safety) and avoid unmaintained pins.

2) Actions
- requirements.txt (runtime):
  - Ensure PyYAML >= 5.1 (safe_load available and wheels for new Pythons). Prefer a modern stable (e.g., 6.x) if compatible with the codebase.
  - Keep other runtime deps minimal; only pin when needed for compatibility.
- requirements-dev.txt (dev/test):
  - Pin testing tools (pytest, coverage/pytest-cov) to versions supporting Python 3.12.
  - Ensure client extras used in tests are present (e.g., requests, flask, tornado, werkzeug) with versions that install on 3.12.
- Consider an upper pin for breaking changes only if proven necessary by tests; otherwise prefer caret/compatible pins.
- Optionally add a constraints.txt to stabilize indirect dependencies if flakiness is observed.

### Sources to reuse
- manatlan/develop and EngMahmoudTaha/develop: both adjust requirements to be compatible with newer Python versions; lift versions cautiously and align to our 3.8/3.10/3.12 matrix.

3) Python compatibility metadata (optional tidy)
- If adjusting packaging later, set python_requires=">=3.8" and update Trove classifiers in setup.py (or pyproject.toml if migrated). This specific metadata update can be deferred to the release step.

## C) Test invocation and caching in CI
- Use the project’s documented command:
  - python -m pytest -s -v --cov=pyswagger --cov-config=.coveragerc pyswagger/tests
- Enable pip cache via actions/setup-python to accelerate installs.
- Optionally caching .pytest_cache is unnecessary; rely on pip cache for most gains.

## D) Documentation updates
- README badges:
  - Add GitHub Actions status badge for the test workflow.
  - Optionally keep/remove Travis badge depending on whether it remains active.
- CHANGES.md:
  - Under Unreleased: note addition of GitHub Actions CI and any dependency pin updates.

## E) Acceptance criteria
- GitHub Actions workflows are present and run automatically on PRs and pushes to main branches.
- Test matrix covers Python 3.8, 3.10, and 3.12; all jobs pass.
- requirements*.txt install cleanly on the matrix; no broken pins.
- README and CHANGES.md updated accordingly.

## F) PR contents (recommended)
- Add .github/workflows/python-package.yml (and optionally lint.yml).
- Update requirements.txt and requirements-dev.txt minimally to ensure 3.12 compatibility.
- Update README badge(s) and add CHANGES.md entry.

## Developer checklist (Step 5)
- [ ] Add GitHub Actions test workflow with Python 3.8/3.10/3.12
- [ ] (Optional) Add lint workflow with flake8/pylint
- [ ] Enable pip caching in CI
- [ ] Refresh requirements: ensure PyYAML >= 5.1 and 3.12-compatible test deps
- [ ] Verify local installs and test runs on 3.8/3.10/3.12
- [ ] Update README badges and CHANGES.md (Unreleased)
- [ ] Confirm CI is green on PR and post-merge

## Risks and mitigations
- Risk: Dependency resolution differences across Python versions cause intermittent failures.
  - Mitigation: Use conservative pins and/or constraints; test locally on multiple versions.
- Risk: Lint workflow generates too much churn.
  - Mitigation: Start with warnings-only or a minimal toolset; enforce gradually.
- Risk: Dropping support for older Python versions implicitly.
  - Mitigation: Clearly document supported versions; if older versions must remain, expand matrix and fix pins as needed.

## Definition of done for Step 5
- GitHub Actions test workflow is in place and green across Python 3.8, 3.10, and 3.12.
- Dependencies are minimally refreshed to support the matrix; installs and tests succeed consistently.
- Documentation (README badges and CHANGES.md) updated to reflect CI adoption and dependency notes.

---
