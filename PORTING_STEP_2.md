# Step 2 — Client correctness: multi-value HTTP headers (Flask client)

Date: 2025-11-18 13:11 (local)

This document sits alongside initial_porting_plan.md and PORTING_STEP_1.md and focuses exclusively on correcting client behavior for multi-value HTTP headers in the Flask testing client integration.

## Objectives
- Align client behavior with modern Flask/Werkzeug and HTTP semantics: when a response includes repeated headers with the same name (e.g., `Set-Cookie`, `Link`, `Warning`), expose them as a list instead of collapsing/overwriting them.
- Preserve single-value headers as strings to avoid unnecessary breakage.

## Scope
- Primary target: Flask native testing client adapter and any response wrapper code used by it.
- Optional parity checks for other clients (`requests`, `tornado`, `webapp2`) only if changes are trivial and low risk; otherwise defer and document.
- Tests and documentation updates limited to header retrieval behavior.

---

## A) Implement multi-value header handling in the Flask client

1) Locate the Flask client adapter (commonly under `pyswagger/contrib/client/flask.py` or equivalent response wrapper).
2) When building the headers mapping from Flask’s `Headers`/`EnvironHeaders` (Werkzeug MultiDict-like objects), aggregate duplicates using `getlist`:

```python
# illustration only
normalized = {}
for key in resp.headers.keys():  # unique, case-preserved keys
    values = resp.headers.getlist(key)
    normalized[key] = values if len(values) > 1 else values[0]

# ensure header name lookups remain case-insensitive if the client currently guarantees that
```

3) Preserve `Set-Cookie` semantics: never join multiple cookie headers by comma. Always return a list when there are multiple `Set-Cookie` fields.
4) Maintain the existing headers container/type (dict-like). Only the value type should vary between `str` and `list[str]` based on multiplicity.
5) Ensure case-insensitive matching of header names is preserved (combine `link` and `Link` under one logical key).

### Sources to reuse
- EngMahmoudTaha/develop: commit `f2b5756` implements multi-value header handling in the Flask client adapter.

### Edge cases to cover
- Multiple duplicate header lines with varying case (e.g., `link` vs `Link`): treat as the same key per RFC 9110.
- Headers that may be comma-separated in a single field line (e.g., `Accept`, `Cache-Control`) but arrive as separate lines: still return a list; downstream code can join if appropriate.

---

## B) Tests to add/update

Add unit tests under the Flask client tests (e.g., `pyswagger/tests/contrib/client/test_flask.py`):

- Multiple duplicates
  - A route that returns two `X-Thing` headers: `X-Thing: a` and `X-Thing: b`.
  - Assert: `headers['X-Thing'] == ['a', 'b']` (order preserved).

- `Set-Cookie`
  - A route that returns two cookies via two `Set-Cookie` headers.
  - Assert: `headers['Set-Cookie']` is a list with two cookie strings. Optionally assert cookie jar behavior if the client exposes one.

- Single value remains a string
  - A route returning a single `ETag` header.
  - Assert: `headers['ETag']` is a `str`.

- Case insensitivity
  - A route that emits `link` and `Link` headers.
  - Assert: they are combined and surfaced as one logical header key with a list of values.

If prior tests assumed a single string when duplicates existed, update expectations accordingly.

### Sources to reuse
- EngMahmoudTaha/develop: commit `333a27a` updates tests to assert list values for duplicate headers.

---

## C) Optional parity checks (only if low risk)

- `requests` client:
  - Requests typically surfaces a case-insensitive dict of final header values (duplicates may be collapsed, except `Set-Cookie`, which is accessible via `response.cookies`). If non-trivial, document differences and keep the Flask change only in this step.

- `tornado`/`webapp2` clients:
  - If their response objects provide `get_list`/`get_all`, mirror the Flask behavior; otherwise, defer.

---

## D) Backward compatibility and configuration

- Expected impact: downstream code that assumed `str` for headers with duplicates may now receive `list[str]`.
- Mitigations:
  - Document the change clearly in `CHANGES.md` under Unreleased.
  - Optionally add an opt-out flag on the Flask client (e.g., `multi_value_headers=False`) defaulting to the new correct behavior; consider deprecating the flag later.

---

## E) Documentation updates

- Update or add a short section in `docs/md/tutorial/customized_headers.md` (or equivalent) describing header access patterns:
  - Single header → `str`
  - Repeated header → `list[str]`
  - Examples for reading `Set-Cookie` and `Link`.
- Add a note to `CHANGES.md` summarizing the behavior change and migration guidance.

---

## F) Acceptance criteria

- Flask client returns `list[str]` for headers that appear multiple times; returns `str` for single occurrences.
- Tests cover duplicates, `Set-Cookie`, single-value headers, and case normalization.
- No regressions in existing client tests; suite remains green on supported Python versions.
- Documentation and `CHANGES.md` entries added.

---

## G) PR contents (what to include)

- Code changes in the Flask client header parsing path.
- New/updated unit tests as outlined.
- Documentation updates and `CHANGES.md` entry.

---

## Developer checklist (copy/paste for Step 2)

- [ ] Implement `getlist`-based aggregation of headers in Flask client
- [ ] Preserve `str` for single headers; `list[str]` for duplicates
- [ ] Ensure case-insensitive lookup remains consistent
- [ ] Add tests: duplicate headers, `Set-Cookie`, single header, mixed-case keys
- [ ] Update docs (`customized_headers.md`) and `CHANGES.md`
- [ ] Run full test suite across supported Python versions

---

## Risks and mitigations

- Risk: Downstream code expecting `str` for duplicates breaks.
  - Mitigation: Clear docs and changelog; optional opt-out flag; suggest normalization idiom (e.g., `val if isinstance(val, str) else ','.join(val)`), though for `Set-Cookie` joining is discouraged.

- Risk: Inconsistent behavior across clients.
  - Mitigation: Document in this step; plan parity adjustments for other clients in a later step if needed.

---

## Definition of done for Step 2

- Flask client correctly surfaces multi-value headers as lists; singles as strings.
- Comprehensive tests pass and guard against regressions.
- Documentation and changelog updated.

---
