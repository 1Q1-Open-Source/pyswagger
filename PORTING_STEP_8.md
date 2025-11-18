# Step 8 — Release preparation (Git-based distribution)

Date: 2025-11-18 13:59 (local)

This document captures only the eighth step from the initial porting plan: preparing a releasable state for Git-based installation (no PyPI/TestPyPI publication). It focuses on finalizing version metadata and changelog, creating and pushing an annotated tag, drafting a GitHub Release, and verifying installation via pip from a git URL (tag or commit) and from the GitHub tag archive URL. No new features are implemented in this step.

---

## Objectives
- Ensure version metadata and changelog are finalized and consistent.
- Create and push an annotated git tag for the new version and draft a GitHub Release.
- Verify installation on supported Python versions directly from a git URL (by tag and by commit hash), and from the GitHub tag archive URL.

---

## Scope
- In scope: version bump (if not already done in Step 7), changelog finalization, git tagging, GitHub Release notes, and VCS install verification.
- Out of scope: PyPI/TestPyPI publication, twine uploads, packaging-specific metadata tuning for PyPI.

### Sources to reuse
- None directly applicable from forks; most prior art targets PyPI/TestPyPI via twine. This step focuses on Git-based tagging and verification.

---

## A) Pre-release consolidation
1) Confirm Steps 1–7 are merged to the release branch and CI is green on the matrix (3.8/3.10/3.12).
2) Finalize CHANGES.md:
   - Move items from Unreleased into a new versioned section (e.g., v0.9.0 – YYYY-MM-DD).
   - Keep a fresh Unreleased section at the top.
3) Version bump (if not already applied in Step 7):
   - Update the canonical version in code (typically `pyswagger/__init__.py` as `__version__`).
   - If `setup.py` is present and used, update its version string and any classifiers/python_requires to match. Although we are not publishing to PyPI, keeping metadata consistent avoids confusion when users install from source.
   - Ensure versions match and are semantically correct for the planned release (likely a minor bump per Step 7 guidance).
4) Verify LICENSE year(s) and author/maintainer info are up to date.

---

## B) Verify installation from Git (primary path)
Create a fresh virtual environment and install from the repository using pip’s VCS support.

1) Install from a tagged release (recommended for consumers):
```bash
python -m venv .venv-vcs-test
. .venv-vcs-test/bin/activate  # on Windows: .venv-vcs-test\Scripts\activate
python -m pip install --upgrade pip

# PEP 508 direct reference
python -m pip install "pyswagger @ git+https://github.com/1Q1-Open-Source/pyswagger.git@v<NEW_VERSION>"

# or legacy form
python -m pip install git+https://github.com/1Q1-Open-Source/pyswagger.git@v<NEW_VERSION>
```

2) Install from a specific commit (pinning for reproducibility):
```bash
python -m pip install "pyswagger @ git+https://github.com/1Q1-Open-Source/pyswagger.git@<COMMIT_SHA>"
```

3) Install from the GitHub tag archive URL (no git client required):
```bash
python -m pip install https://github.com/1Q1-Open-Source/pyswagger/archive/refs/tags/v<NEW_VERSION>.zip
```

4) Smoke test imports after installation:
```bash
python - <<'PY'
import pyswagger, sys
print('pyswagger', getattr(pyswagger, '__version__', 'unknown'))
PY
```

---

Optionally, run a minimal quick-start to ensure core imports and a simple client path work without network I/O (mock if necessary).

---

## C) (Optional) Local artifact build for internal validation
While distribution is via Git, you may optionally build local artifacts to validate packaging integrity (not for upload):
```bash
python -m pip install --upgrade build
python -m build  # produces dist/*.tar.gz and dist/*.whl
```
Then install the local wheel in a clean venv and smoke test imports as above. This helps detect missing files in MANIFEST.in even if you don’t publish to PyPI.

---

## D) Tagging and release notes
1) Create a signed (or annotated) tag:
```bash
git tag -s v<NEW_VERSION> -m "pyswagger <NEW_VERSION>"
git push origin v<NEW_VERSION>
```
2) Draft a GitHub Release using CHANGES.md content for this version:
- Title: `v<NEW_VERSION>`
- Body: Summarize Added/Changed/Fixed/Security and migration notes.
- Attach optional artifacts if desired (sdist/wheel built locally), but Git remains the canonical distribution.

---

## E) (Out of scope) PyPI/TestPyPI publication
This project is distributed via Git only. Do not upload to PyPI/TestPyPI as part of this step. If this policy changes later, re-introduce packaging guidance in a future document.

---

## F) Post-release housekeeping
- Update any documentation pages that reference the latest version (badges, links), if applicable.
- Close the milestone and link merged PRs/issues to the release.
- Open a new "Unreleased" milestone for ongoing work.

---

## Acceptance criteria
- CHANGES.md has a finalized section for `<NEW_VERSION>` with date; Unreleased is reset.
- Version metadata in code (and setup.py if present) matches the released version.
- Clean-venv install via pip from the git URL succeeds for:
  - tagged ref: `pyswagger @ git+https://github.com/1Q1-Open-Source/pyswagger.git@v<NEW_VERSION>`
  - commit ref: `pyswagger @ git+https://github.com/1Q1-Open-Source/pyswagger.git@<COMMIT_SHA>`
  - tag archive URL: `https://github.com/1Q1-Open-Source/pyswagger/archive/refs/tags/v<NEW_VERSION>.zip`
- Git tag `v<NEW_VERSION>` exists and is pushed; GitHub Release drafted/published.

---

## PR contents (recommended)
- CHANGES.md finalized for the release (with date), plus Unreleased reset.
- Version bump in code and setup.py (if not done in Step 7).
- (Optional) Adjusted MANIFEST.in if local packaging validation revealed missing files.
- A short release checklist in the PR description referencing this document.

---

## Developer checklist (Step 8)
- [ ] Ensure Steps 1–7 are merged; CI is green on 3.8/3.10/3.12
- [ ] Finalize CHANGES.md for `<NEW_VERSION>` and date; reset Unreleased
- [ ] Update version metadata in code and setup.py (if present)
- [ ] Clean venv install from git tag and commit refs; smoke test imports
- [ ] (Optional) Build local sdist/wheel to validate MANIFEST and install locally
- [ ] Create signed/annotated git tag `v<NEW_VERSION>` and push
- [ ] Draft GitHub Release with notes from CHANGES.md
- [ ] Post-release housekeeping (milestone, docs badges/links)

---

## Risks and mitigations
- Risk: VCS install requires build tooling on the consumer’s machine (setuptools/wheel); missing build deps can fail installation.
  - Mitigation: Keep runtime build requirements minimal; document prerequisites in README.
- Risk: GitHub rate limits or access restrictions affect installs from CI or private environments.
  - Mitigation: Recommend using tags and vendored mirrors if necessary; for private repos, document SSH or tokenized URLs.
- Risk: Version mismatch between code and setup.py when installing from source.
  - Mitigation: Maintain a single source of truth for version or verify consistency as part of tagging.

---

## Definition of done for Step 8
- Clean-venv installs succeed from git URL (tag and commit) and from the tag archive URL on supported Python versions.
- Versioned tag is pushed; GitHub Release with accurate notes is available.
- CHANGES.md finalized and version metadata consistent.

---
