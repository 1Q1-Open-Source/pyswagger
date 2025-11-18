# Step 3 — Format and codec enhancements (HAL JSON + UUID format)

Date: 2025-11-18 13:17 (local)

This step implements two format/codec items from the initial plan: adding support for the `application/hal+json` MIME type and fixing UUID handling so values with `format: uuid` are validated correctly and serialized as strings. It is intentionally scoped to be low risk and easily testable.

---

## Objectives
- Register and support `application/hal+json` responses/requests by leveraging the existing JSON codec (HAL is a JSON-based media type).
- Ensure schemas with `type: string` and `format: uuid`:
  - validate incoming values according to RFC 4122 UUID syntax (case-insensitive, hyphenated form), and
  - serialize outbound values as strings (convert `uuid.UUID` objects to canonical string form), avoiding behavior changes for non-UUID strings.

---

## Scope
- Code paths for MIME codec registration/selection and primitive/format handling (UUID).
- Unit tests targeting both features.
- Minimal documentation updates (tutorial/reference + changelog).
- No behavioral changes to other codecs or formats.

---

## A) Add `application/hal+json` codec

### Approach
- Implement a HAL JSON codec that reuses the existing JSON load/dump behavior and simply registers the additional content type. This yields broad compatibility for APIs returning HAL without adding HAL-specific link traversal features (which can be considered later if desired).

### Implementation outline
- Create a small codec class that inherits the existing JSON codec and sets `content_types` (or equivalent registry metadata) to include `application/hal+json`.
- Register the codec in the global codec registry so negotiation picks it when `Content-Type`/`Accept` includes `application/hal+json`.

```python
# sketch: adjust names/paths to match your project’s codec API
from .json import JsonCodec  # existing JSON codec

class HalJsonCodec(JsonCodec):
    content_types = ("application/hal+json",)
    # Inherit load/dump from JsonCodec; no HAL-specific logic required initially.

# Registration (e.g., in codec registry module)
register_codec(HalJsonCodec)
```

### Sources to reuse
- manatlan/develop: commit `1d3e697` adds support for `application/hal+json` by registering a HAL codec that reuses JSON semantics.

### Tests to add
- Content negotiation picks the HAL codec when response `Content-Type: application/hal+json` is present.
- Round-trip load/dump behaves identically to JSON for typical bodies, including HAL-specific fields like `_links` and `_embedded` (they should be preserved as-is).
- If your framework normalizes charsets (e.g., `application/hal+json; charset=utf-8`), verify matching works with parameters present.

### Backward compatibility
- None expected; this only adds support for an additional MIME type while reusing JSON semantics.

---

## B) UUID `format` handling (validate, serialize as string)

### Approach
- Treat OpenAPI/Swagger `type: string, format: uuid` as a string value with stricter validation and predictable serialization.
- Validation should accept any RFC 4122 UUID variant that Python’s `uuid.UUID` can parse from a hyphenated string (case-insensitive). Non-hyphenated 32-hex forms are typically not accepted by OpenAPI 2.0 examples; prefer the 36-character hyphenated form to avoid false positives.
- Serialization: if a caller supplies a `uuid.UUID` instance, convert to `str(value)` (canonical lowercase, hyphenated). If a caller supplies a valid UUID string, pass through unchanged.

### Implementation outline
- In your string-format handling (primitive factory or validator layer), register a handler for the `uuid` format.

```python
# sketch: adapt to your factory/validator APIs
import uuid

def _is_uuid_string(value: str) -> bool:
    if not isinstance(value, str):
        return False
    try:
        # Strict hyphenated form check (length 36 with 4 hyphens)
        if len(value) != 36:
            return False
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False

# Validation hook for format="uuid"
def validate_uuid(value):
    return _is_uuid_string(value) or isinstance(value, uuid.UUID)

# Coercion/serialization hook for outbound data
# Returns a string (canonical) if value is uuid.UUID; otherwise returns value unchanged
# (assuming it’s a valid UUID string).

def serialize_uuid(value):
    if isinstance(value, uuid.UUID):
        return str(value)  # canonical hyphenated lowercase
    return value

# Registration (pseudocode)
# PrimFactory.register("string", format="uuid", validator=validate_uuid, serializer=serialize_uuid)
```

- If your framework separates inbound (response) decoding and outbound (request) encoding:
  - Inbound: leave UUIDs as strings (do not convert to `uuid.UUID` to avoid API-breaking changes unless you already do that for other formats).
  - Outbound: allow callers to pass `uuid.UUID` or valid strings; always emit a valid string.

### Sources to reuse
- post-cyberlabs/openapi: commit `0eb0517` corrects UUID format validation and ensures outbound serialization to strings.

### Tests to add
- Validation (positive cases):
  - `"550e8400-e29b-41d4-a716-446655440000"` (v4 example)
  - Uppercase hex characters still validate (case-insensitive)
  - A `uuid.UUID("550e8400-e29b-41d4-a716-446655440000")` instance passes validation
- Validation (negative cases):
  - Wrong length (e.g., `"550e8400e29b41d4a716446655440000"` without hyphens)
  - Invalid hex characters
  - Not a string/UUID (e.g., integers, dicts)
- Serialization:
  - Passing a `uuid.UUID` yields its canonical string via `str(value)`
  - Passing a valid UUID string is returned unchanged
- Response decoding:
  - When server responds with a UUID string under a schema with `format: uuid`, decoded value remains a string and matches the original.

### Backward compatibility
- Do not convert incoming UUID strings into `uuid.UUID` automatically; continue exposing strings to avoid breaking callers.
- Preserve case of input strings on the decoding path; only `uuid.UUID` objects (when supplied) are normalized to `str()` for outbound serialization.

---

## Documentation updates
- Add/update a short section in the MIME tutorial/reference to state that `application/hal+json` is supported and uses JSON semantics.
- Add/update a section in the data types/format reference describing `format: uuid` behavior:
  - Valid shapes, examples, and that outbound `uuid.UUID` will be converted to strings.
- Add changelog entries under Unreleased summarizing HAL support and the UUID format fix.

---

## Acceptance criteria
- Content negotiation recognizes `application/hal+json` and uses the HAL codec that round-trips bodies like JSON.
- UUID format handling:
  - Valid UUID strings and `uuid.UUID` instances pass validation; invalid values are rejected.
  - Outbound serialization returns strings for UUIDs; inbound decoding yields strings (no silent type change).
- New tests for both features pass across supported Python versions (3.8–3.12).
- No regressions in existing codec/format tests.

---

## PR contents (recommended slicing)
- PR 1 — HAL JSON support
  - Codec class + registry change
  - Tests for negotiation and round-trip
  - Docs and changelog updates
- PR 2 — UUID format fix
  - Validator/serializer registration and any minor helper utilities
  - Unit tests (positive/negative + serialization)
  - Docs and changelog updates

---

## Developer checklist (copy/paste)
- HAL codec
  - [ ] Add `HalJsonCodec` inheriting from existing JSON codec
  - [ ] Register `application/hal+json` in the codec registry
  - [ ] Tests: negotiation + round-trip (with `_links`, `_embedded` present)
  - [ ] Docs: mention HAL support; `CHANGES.md` updated
- UUID format
  - [ ] Register validator/serializer for `format: uuid`
  - [ ] Tests: valid/invalid cases; `uuid.UUID` serialization to string; inbound remains string
  - [ ] Docs: data type/format section; `CHANGES.md` updated
- General
  - [ ] Run full test suite on 3.8/3.10/3.12 and ensure green

---

## Risks and mitigations
- HAL specifics not honored (links/embedded semantics):
  - Mitigation: Document that initial support is JSON-equivalent; deeper HAL navigation can be considered later without breaking changes.
- UUID normalization surprises:
  - Mitigation: Only normalize `uuid.UUID` instances on outbound serialization; leave inbound strings unchanged; document behavior.

---

## Definition of done for Step 3
- `application/hal+json` accepted in content negotiation; bodies load/dump like JSON; tests validate behavior (including with parameters like `; charset=utf-8`).
- `format: uuid` values validate correctly; outbound `uuid.UUID` is serialized to its string form; inbound strings remain strings.
- Documentation and changelog updated; test suite green on supported Python versions.

---
