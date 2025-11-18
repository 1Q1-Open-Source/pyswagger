# Step 1 — Security and Python Compatibility (detailed implementation plan)

Date: 2025-11-18 13:02 (local)

This document sits alongside initial_porting_plan.md and focuses exclusively on hardening YAML usage and making the codebase work cleanly on Python 3.10–3.12. It is designed to be executed as a small, low‑risk series of PRs.

## Objectives
- Eliminate unsafe YAML loading throughout the codebase.
- Remove deprecated or removed APIs that fail on Python 3.10+ (`collections` ABCs and `imp`).
- Normalize fragile regexes (notably ISO‑8601) to raw strings for cross‑version consistency.
- Make minimal, surgical updates to dependencies to keep the current test suite green on 3.8–3.12.

## Scope
- Code and tests only; no public API behavior changes beyond safer YAML parsing and import compatibility.
- Keep existing behavior where possible; add targeted tests to prevent regressions.

---

## A) Replace unsafe YAML usage

### What to do
- Replace every `yaml.load(...)` with `yaml.safe_load(...)` (or `yaml.safe_load_all` for streams).
- If dumping YAML, prefer `yaml.safe_dump(...)` unless arbitrary Python objects are truly required.
- Remove explicit `Loader=` parameters that reference unsafe loaders (e.g., `yaml.Loader`, `yaml.FullLoader`) unless documented and strictly required.

### Implementation details
```python
import yaml
data = yaml.safe_load(text_or_stream)
```

Stream/multi‑document YAML:
```python
docs = list(yaml.safe_load_all(stream))
```

If there are custom YAML tags used by the project, register safe constructors on top of `SafeLoader` rather than reverting to the unsafe loader:
```python
class _Loader(yaml.SafeLoader):
    pass

def construct_my_tag(loader, node):
    # construct in a controlled/safe way
    return loader.construct_scalar(node)

_Loader.add_constructor('!mytag', construct_my_tag)
data = yaml.load(stream, Loader=_Loader)
```

### Code search checklist
- Search patterns: `yaml.load(`, `Loader=`, `FullLoader`, `UnsafeLoader`, `yaml.dump(`.
- Likely locations: configuration readers, spec loaders, test fixtures under `pyswagger/tests`.

### Sources to reuse
- EngMahmoudTaha/develop: commit `a0d7a30` (replace yaml.load with yaml.safe_load).
- benkilimnik/develop: commit `8116389` (yaml.safe_load adoption).
- manatlan/develop: multiple commits around PyYAML pinning/py3.12 compatibility (useful as guidance for Step 5 dependency updates).

### Tests to add/adjust
- Add a regression test that attempts to load a YAML payload with a Python object constructor (e.g., `!!python/object/apply`) and assert it raises or is parsed as plain data (no code execution).
- Ensure existing YAML‑based spec loading tests still pass.

### Acceptance criteria
- No remaining uses of `yaml.load` without a safe loader.
- All YAML parsing unit tests pass on Python 3.8–3.12.

---

## B) Update deprecated ABC imports to `collections.abc`

### What to do
- Replace imports like `from collections import Mapping, MutableMapping, Sequence` with `from collections.abc import Mapping, MutableMapping, Sequence`.

### Implementation details
```python
from collections.abc import Mapping, MutableMapping, Sequence
```

### Code search checklist
- Search patterns: `from collections import`, `collections.Mapping`, `collections.MutableMapping`, `collections.Sequence`.

### Sources to reuse
- EngMahmoudTaha/develop: commit `9251257` (move ABC imports to collections.abc).
- benkilimnik/develop: commit `0e0c476` (MutableMapping import fix).
- manatlan/develop: multiple small fixes for collections.abc across files.

### Tests to add/adjust
- None typically required; a full test run on 3.10+ is sufficient to catch missing imports.

### Acceptance criteria
- Zero references to ABCs from `collections` (non‑abc) across the repo.

---

## C) Replace `imp` with `importlib`

### What to do
- Remove usage of the deprecated `imp` module, which is removed in newer Python versions.

### Implementation details
Dynamic import by module name:
```python
import importlib
mod = importlib.import_module(module_name)
```

Import from a file path:
```python
import importlib.util
import sys

spec = importlib.util.spec_from_file_location(mod_name, file_path)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)
sys.modules[mod_name] = mod
```

### Code search checklist
- Search patterns: `import imp`, `imp.load_module`, `imp.find_module`.

### Sources to reuse
- EngMahmoudTaha/develop: commit `6d45a1d` (drop imp in favor of importlib and bump version).

### Tests to add/adjust
- If any plugin/module loader exists, add a test exercising dynamic load by name/path on Python 3.12.

### Acceptance criteria
- No imports of `imp`; loaders validated by tests where applicable.

---

## D) Normalize fragile regexes to raw strings (ISO‑8601 and friends)

### What to do
- Identify date/time or escape‑heavy regex literals and convert them to raw strings: `r"..."`.
- Ensure escaping is correct and tests cover typical/edge cases.

### Implementation details
```python
# before
ISO8601 = "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$"
# after
ISO8601 = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
```

### Code search checklist
- Search patterns: `\\d{`, `\\w`, `\\s`, `re.compile("`, `re.compile('\\`)`.
- Likely locations: schema validators, format checkers, utility modules.

### Sources to reuse
- EngMahmoudTaha/develop: commit `e271374` (ISO‑8601 regex: convert to raw strings and fix escapes).

### Tests to add/adjust
- Positive/negative tests for ISO‑8601 parsing, including timezone offsets and milliseconds if supported by spec.

### Acceptance criteria
- Regexes use raw strings where appropriate; related tests pass consistently across Python versions.

---

## E) Minimal dependency updates to keep tests green on 3.12

### What to do
- Ensure `PyYAML >= 5.1` (or newer) to have `safe_load` behavior consistent and wheels for 3.12.
- If tests or runtime rely on other packages that break on 3.12, bump minimally to versions that provide 3.12 wheels.

### Implementation details
- Update `requirements.txt` / `requirements-dev.txt` conservatively.
- If the project uses `setup.cfg`/`pyproject.toml`, update `python_requires` and classifiers after test verification (can be deferred to the release step).

### Sources to reuse
- manatlan/develop: py3.12 compatibility and YAML pin updates provide a useful reference for minimal versions that work across new interpreters.

### Tests to add/adjust
- CI matrix (or local tox) across 3.8, 3.10, 3.12. If CI is deferred, run locally and paste results in the PR.

### Acceptance criteria
- Unit tests pass on 3.8–3.12 with the pinned dependency set.

---

## Execution order and PR slicing

1) PR 1 — YAML safety
   - Replace unsafe loads/dumps.
   - Add malicious‑YAML regression test.

2) PR 2 — `collections.abc` imports
   - Replace deprecated ABC imports.

3) PR 3 — `imp` → `importlib`
   - Update dynamic import code; add a loader test if applicable.

4) PR 4 — Regex raw strings
   - Convert fragile regex literals; add ISO‑8601 tests.

5) PR 5 — Minimal dependency bumps (if needed)
   - Pin PyYAML and any other essentials; verify test matrix.

Each PR should include a short section in `CHANGES.md` under “Unreleased”.

---

## Developer checklist (copy/paste)

- Search and replace
  - [ ] `yaml.load(` → `yaml.safe_load(`
  - [ ] `yaml.safe_load_all(` used for multi‑doc streams where needed
  - [ ] Remove unsafe `Loader=` usage unless replaced with a safe custom loader
  - [ ] `from collections import Mapping` → `from collections.abc import Mapping`
  - [ ] Remove all `import imp` usage
  - [ ] Convert escape‑heavy regex strings to raw strings
- Tests
  - [ ] Add malicious YAML regression test
  - [ ] Add/expand ISO‑8601 regex tests
  - [ ] Run full test suite on 3.8/3.10/3.12
- Dependencies
  - [ ] Ensure `PyYAML` version compatible with 3.12
- Documentation
  - [ ] Update `CHANGES.md` for each PR

---

## Risks and mitigations
- YAML with custom tags might rely on unsafe constructors
  - Mitigation: add explicit, safe constructors based on `yaml.SafeLoader` and document the supported tags.
- Dynamic import differences (`imp` vs `importlib`)
  - Mitigation: use the `importlib.util.spec_from_file_location` pattern; add a unit test for the loader.
- Regex behavior changes
  - Mitigation: keep tests strict and mirror documented spec examples.

---

## Definition of done for Step 1
- No uses of `yaml.load` without `SafeLoader`.
- No imports of ABCs from `collections` (only from `collections.abc`).
- No imports of `imp` remain.
- Fragile regexes converted to raw string form with tests proving behavior.
- All tests pass on Python 3.8–3.12.

---
