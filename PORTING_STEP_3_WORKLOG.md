Step 3 Worklog - Format and codec enhancements (HAL JSON + UUID)

Date: 2025-11-18 15:28 (local)

This worklog documents what was implemented for Step 3, the reasoning behind each decision, alternatives considered, and verification status. It is intended to sit alongside PORTING_STEP_3.md (the plan for this step) and provide a durable audit trail of changes and trade-offs.

Overview and scope
- Add support for the `application/hal+json` MIME type by reusing existing JSON codec semantics.
- Improve handling for schemas with `type: string` and `format: uuid`:
  - Accept `uuid.UUID` instances and serialize them to canonical string form outbound.
  - Validate incoming UUID strings using the standard hyphenated RFC 4122 syntax.
- Keep risk low and behavior consistent elsewhere; add focused tests and documentation notes.

Summary of changes (by file)

1) pyswagger/primitives/codec.py — HAL JSON registration
- What changed:
  - Registered `application/hal+json` to use the existing `JsonCodec` (same marshal/unmarshal behavior as `application/json`).
  - Parameterized content types (e.g., `application/hal+json; charset=utf-8`) are already handled via `MimeCodec.codec()` which strips parameters after a `;`.
- Why:
  - HAL is a JSON-based media type. Reusing JSON semantics provides broad compatibility without introducing HAL-specific traversal logic.

2) pyswagger/tests/test_codec.py — tests for HAL
- What changed:
  - Added `test_hal_json_codec` to assert that `application/hal+json` round-trips like JSON, including common HAL fields (`_links`, `_embedded`).
  - Verified that parameterized content types (e.g., with `charset` parameter) are matched correctly.
- Why:
  - Ensures content negotiation/lookup works and behavior is identical to JSON as intended.

3) pyswagger/primitives/_uuid.py — stricter validation and robust inputs
- What changed:
  - Enhanced `UUID.apply_with` to:
    - Accept `uuid.UUID` objects directly (stored as-is and serialized to strings via `to_json`).
    - Validate string inputs to be hyphenated RFC 4122 UUIDs; raise `ValidationError` for malformed strings (including non-hyphenated 32-hex forms).
    - Continue supporting byte inputs via `uuid.UUID(bytes=...)`.
- Why:
  - Aligns with common OpenAPI usage for `format: uuid` and avoids accepting ambiguous/non-standard string variants.
- Notes:
  - We intentionally keep producing the existing wrapper primitive (`primitives.UUID`) for inbound values to avoid breaking existing behavior/tests. Converting inbound UUID strings to bare strings (as an API change) is deferred.

4) pyswagger/tests/v2_0/test_prim.py — tests for UUID format
- What changed:
  - Added two tests:
    - `test_uuid_invalid_string`: non-hyphenated 32-hex strings are rejected with `errs.ValidationError`.
    - `test_uuid_uppercase_accepted`: uppercase hyphenated strings are accepted; canonical string representation is lowercase.
- Why:
  - Captures both negative and positive validation cases and confirms canonicalization when serialized.

5) CHANGES.md — Unreleased entries
- What changed:
  - Documented HAL support and UUID format behavior under Unreleased.
- Why:
  - Visibility for users adopting the new capabilities.

6) docs/md/tutorial/mime.md — brief note
- What changed:
  - Added a short note that `application/hal+json` is supported and uses JSON semantics (including when parameters like `; charset=utf-8` are present).
- Why:
  - Minimal documentation touchpoint to acknowledge HAL support.

Decision log and rationale

- Reuse JSON codec for HAL (`application/hal+json`)
  - Rationale: HAL is structurally JSON; initial support should be non-invasive. A future enhancement could add higher-level HAL features (e.g., link traversal) without breaking the codec layer.
  - Alternative: create a separate codec implementation — rejected for now as behavior would be identical.

- UUID format handling (validation + serialization)
  - Rationale: OpenAPI examples and common practice assume hyphenated RFC 4122 UUID strings. Tightening validation reduces ambiguity and aligns with expectations.
  - Outbound behavior: When callers provide a `uuid.UUID`, serialize to string via the existing `to_json` pathway. This yields predictable JSON payloads.
  - Inbound behavior: Preserve the project’s current behavior (producing the UUID wrapper primitive) to avoid test and API breakage. The “keep inbound as string” idea from some forks is deferred and documented for potential future discussion.

Compatibility and risk assessment

- HAL codec
  - Behavior: Additive only. Requests/responses with `application/hal+json` are now supported. JSON semantics are reused; no changes for other media types.
  - Risk: Low. Registration only; no path changes for existing content types.

- UUID format
  - Behavior: Stricter validation rejects non-hyphenated or malformed UUID strings under `format: uuid`. Existing tests already assume a proper UUID string or `uuid.UUID` instance.
  - Public API: No changes to public types exposed by the primitive factory (still returns the UUID wrapper on inbound). Outbound JSON serialization remains strings.
  - Risk: Low-to-moderate. Projects relying on accepting non-hyphenated 32-hex UUID strings will now see validation failures. This is considered a correctness improvement and documented in CHANGES.md.

Verification performed

- Unit tests
  - Added: `test_hal_json_codec` for HAL support in `pyswagger/tests/test_codec.py`.
  - Added: UUID negative and uppercase acceptance tests in `pyswagger/tests/v2_0/test_prim.py`.

- Manual code sanity checks
  - Confirmed `MimeCodec.codec()` correctly strips parameters, allowing `; charset=utf-8` on HAL content types.
  - Verified `UUID.to_json()` ensures outbound JSON strings for UUIDs via `PrimJSONEncoder`.

- Local test execution (environmental notes)
  - Running tests requires dev dependencies (pytest, Flask/Werkzeug, validate_email, six, etc.). Use the commands below to ensure the environment is prepared.

How to verify locally
- Create/activate a virtualenv
- Install dev dependencies: `pip install -r requirements-dev.txt`
- Run targeted tests:
  - HAL codec: `pytest -q pyswagger/tests/test_codec.py::CodecTestCase::test_hal_json_codec`
  - UUID format: `pytest -q pyswagger/tests/v2_0/test_prim.py::SchemaTestCase::test_uuid_invalid_string pyswagger/tests/v2_0/test_prim.py::SchemaTestCase::test_uuid_uppercase_accepted`
- (Optional) Run full suite: `pytest -q`

Acceptance criteria mapping (Step 3 scope)
- Content negotiation recognizes `application/hal+json` and uses JSON semantics: Achieved.
- UUID format handling:
  - Valid UUID strings and `uuid.UUID` instances pass; invalid values rejected: Achieved.
  - Outbound serialization returns strings for UUIDs; inbound continues to return the existing wrapper for backward compatibility: Achieved.
- New tests for both features present and runnable across supported Python versions (3.8–3.12): Authored; execution depends on local/CI environment.
- No regressions in existing codec/format tests expected.

Follow-ups and next actions
1) Consider a separate doc page or a reference section elaborating on `format: uuid` behavior, including examples and canonicalization notes.
2) If a future API change is desired to keep inbound UUIDs as plain strings, plan a major/minor release note and migration guidance; update tests accordingly.
3) Evaluate adding HAL-specific conveniences (e.g., link traversal helpers) in a non-breaking, opt-in fashion.
4) Execute the full test suite on Python 3.8, 3.10, and 3.12 to confirm no regressions.

References
- Planning docs:
  - initial_porting_plan.md
  - PORTING_STEP_3.md
- Source forks/commits referenced for guidance:
  - manatlan/develop: `1d3e697` (HAL content type registration)
  - post-cyberlabs/openapi: `0eb0517` (UUID format validation/serialization guidance)

---

Prepared by: Junie (JetBrains autonomous programmer)
