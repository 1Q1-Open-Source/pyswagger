# Step 6 — Testing and validation

Date: 2025-11-18 13:33 (local)

This document captures only the sixth step from the initial porting plan: run and expand tests to validate the work from earlier steps across supported Python versions. This step adds and refines tests; it does not change runtime behavior (beyond test-only fixtures/helpers).

---

## Objectives
- Verify that previously ported changes function correctly on Python 3.8, 3.10, and 3.12.
- Add targeted regression tests for areas modified in Steps 1–4 (YAML safety, import/regex compat, Flask header behavior, HAL codec, UUID format, renderer presets).
- Improve determinism and reduce test flakiness (especially around randomness and time).

---

## Scope
- In scope: unit and small integration tests, fixtures, and test utilities; guidance for running the matrix locally and in CI.
- Out of scope: CI workflow definitions (Step 5), feature implementation (Steps 1–4), documentation and release notes (covered elsewhere).

---

## A) Test matrix and environments
1) Python versions: 3.8, 3.10, 3.12 (align with CI).
2) Local execution guidance:
   - Preferred command (as in README):
     - `python -m pytest -s -v --cov=pyswagger --cov-config=.coveragerc pyswagger/tests`
   - Optional: use `pyenv`/`tox` to validate multiple interpreters locally.
3) Ensure optional client dependencies needed by tests are installed (requests, flask, werkzeug, tornado) as specified in requirements-dev.txt.

---

## B) Unit tests to add/update (by area)

### 1) YAML safety (Step 1)
- Add a regression test that attempts to load a malicious YAML payload (e.g., using `!!python/object/apply` or similar) through the project’s spec/config loading path and asserts that it is either rejected or treated as plain data without execution.
- Confirm that benign YAML specs under `pyswagger/tests/data` still load successfully.

### 2) Import and ABC compatibility (Step 1)
- Add a smoke test that imports modules known to have moved ABC imports to `collections.abc` and ensures no ImportError on Python 3.10+.
- If a dynamic module loader exists, rely on tests in section 3 (Importlib loader).

### 3) `imp` → `importlib` loader (Step 1)
- If the project includes a dynamic module loading utility:
  - Create a temporary module file at runtime in a temp directory.
  - Use the updated importlib-based loader to import it.
  - Assert functions/attributes are accessible and module is present in `sys.modules`.
- If no such utility exists, skip with a clear reason (do not invent runtime code in test).

### 4) Regex normalization (ISO‑8601 and friends) (Step 1)
- Add explicit positive cases: e.g., `2020-02-29T12:34:56Z`, with fractional seconds, and timezone offsets like `+08:00` and `-05:30` if supported by the implementation.
- Add negative cases: bad months/days, missing `T`, invalid separators, wrong lengths.
- Ensure regex constants are raw-string backed and work consistently across Pythons.

### 5) Flask client multi-value headers (Step 2)
- Duplicate headers:
  - Route returns `X-Thing: a` and `X-Thing: b`; expect `headers['X-Thing'] == ['a','b']`.
- Set-Cookie:
  - Route returns two cookies via two `Set-Cookie` headers; expect a list of two strings under `headers['Set-Cookie']`.
- Single value remains string:
  - Route returns a single `ETag`; expect `str`.
- Case-insensitive merge:
  - Route emits `link` and `Link`; assert combined under one logical key with both values in order.

### Sources to reuse
- EngMahmoudTaha/develop: commit `333a27a` contains updated tests illustrating expectations for duplicate headers; adapt patterns to our test suite.

### 6) HAL JSON codec (Step 3)
- Content negotiation:
  - When `Content-Type: application/hal+json` (with and without `; charset=utf-8`), ensure the HAL codec is selected.
- Round-trip:
  - Bodies containing `_links` and `_embedded` round-trip via load/dump with no mutation relative to plain JSON semantics.

### 7) UUID format handling (Step 3)
- Validation (positives):
  - Hyphenated RFC 4122 string (lower/upper case) and a `uuid.UUID` instance should pass.
- Validation (negatives):
  - Non-hyphenated 32-hex, invalid hex chars, wrong length, and non-string/non-UUID types should fail.
- Serialization:
  - Outbound `uuid.UUID` converts to canonical string; valid strings pass through unchanged.
- Decoding:
  - Inbound values under `format: uuid` remain strings (no auto-conversion), preserving case.

### 8) Renderer presets (Step 4)
- Minimal preset required-only:
  - For a schema with required and optional properties, minimal preset omits optionals; classic may include them.
- Bounds respected:
  - Arrays/strings respect lowered caps under minimal preset.
- Parameter omission:
  - `render_all` skips optional parameters with minimal preset.
- Template overrides:
  - `object_template` and `parameter_template` override values even under minimal preset.
- Non-regression for classic:
  - Existing renderer tests remain valid without changes.

---

## C) Integration tests (small end-to-end)
- Load representative Swagger 2.0 specs from `pyswagger/tests/data/v2_0` and:
  - Invoke renderer to create example payloads using both presets.
  - Exercise request/response encode/decode cycles for JSON and HAL content types.
  - Validate UUID fields when present according to the registered format.
- Use the Flask test client for local HTTP tests; avoid real network I/O.

---

## D) Determinism and flakiness controls
- Seeding randomness:
  - In tests that depend on random output from the renderer, call `random.seed(0)` before generation.
- Time-dependent behavior:
  - Prefer fixed timestamps; optionally use utilities like `freezegun` only if already in dev deps (do not add new deps in this step unless necessary).
- Networking:
  - Avoid external network calls; use local Flask client or pure in-memory operations.
- Platform variance:
  - Normalize path separators and line endings in assertions where applicable.

---

## E) How to run
- Local: `python -m pytest -s -v --cov=pyswagger --cov-config=.coveragerc pyswagger/tests`
- CI: Covered in Step 5; ensure matrix runs for 3.8/3.10/3.12 are green.

---

## Acceptance criteria
- New/updated tests described above are implemented and passing.
- Entire test suite passes on Python 3.8, 3.10, and 3.12 in CI and locally.
- No new flaky tests (multiple consecutive runs are stable).
- No reliance on external network connectivity in tests.

---

## PR contents (recommended)
- Test files and fixtures only (plus minimal helper utilities under tests if needed).
- No runtime code changes except test-only helpers.
- Add a short Unreleased note in `CHANGES.md` summarizing test coverage improvements (optional).

---

## Developer checklist (Step 6)
- [ ] Add malicious YAML regression test; verify benign YAML loads.
- [ ] Add import/ABC compatibility smoke test on 3.10+ (no ImportError).
- [ ] Add importlib loader test if applicable; skip otherwise with reason.
- [ ] Add ISO‑8601 positive/negative tests.
- [ ] Add Flask multi-value headers tests (duplicates, Set-Cookie, single, case-insensitive).
- [ ] Add HAL codec negotiation and round-trip tests (with/without charset param).
- [ ] Add UUID format tests (validate + serialize; inbound remains string).
- [ ] Add renderer preset tests (required-only, bounds, templates, non-regression for classic).
- [ ] Add small integration tests over sample specs; avoid network.
- [ ] Ensure determinism: seed randomness/time where necessary.
- [ ] Run full suite on 3.8/3.10/3.12; confirm CI is green.

---

## Risks and mitigations
- Risk: Tests inadvertently depend on platform or timing.
  - Mitigation: Normalize assertions; use seeds and fixed timestamps.
- Risk: Introducing tests that assume feature implementations not yet merged.
  - Mitigation: Gate tests to align strictly with Steps 1–4; skip or xfail clearly with issue references if a feature is not yet implemented.

---

## Definition of done for Step 6
- Targeted tests for Steps 1–4 exist and pass.
- Test suite is deterministic and stable across supported Python versions.
- CI matrix (from Step 5) is green with the new tests.

---
