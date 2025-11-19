## Changes

### Unreleased

- CI and dependency refresh (Step 5)
  - Add GitHub Actions workflow to run tests on Python 3.8, 3.10, and 3.12 with pip caching.
  - Refresh requirements:
    - Runtime: add explicit `PyYAML>=6.0` (safe_load available on all supported Pythons).
    - Dev/Test: update to Python 3.12-compatible tools (`pytest>=7.4`, `pytest-cov>=4.1`, `Flask>=2.3`, `tornado>=6.2`, `httpretty>=1.1.4`, `requests>=2.28`, `Sphinx>=7.2`).
    - Remove legacy/unmaintained dev deps (`pudb`, `webapp2`).
  - README: add GitHub Actions CI badge (keep legacy Travis badge for transition).
  - Local testing: add `pytest.ini` (register markers, set testpaths) and `tox.ini` (py38/py310/py312) so `pytest` and `tox` work out-of-the-box; make legacy `webapp2` tests import-safe and auto-skipping on Python 3.

- Flask test client: preserve multi-value response headers
  - When a Flask response includes repeated headers with the same name (e.g., `Set-Cookie`, `Link`), the client now forwards all occurrences to the core Response object instead of collapsing/overwriting them.
  - Response.header continues to expose values as lists (existing API), e.g., `resp.header['X-Thing'] == ['a','b']`. Single headers remain single-item lists for backward compatibility.
  - Case-insensitive header aggregation is improved to ensure mixed-case duplicates (e.g., `link` and `Link`) are combined.

- Codec and format enhancements (Step 3)
  - Add support for `application/hal+json` by reusing JSON codec semantics for marshal/unmarshal (including parameterized content types like `; charset=utf-8`).
  - Improve UUID format handling for `type: string, format: uuid`:
    - Accept `uuid.UUID` instances directly, serializing outbound values to canonical strings.
    - Validate UUID strings using the standard hyphenated RFC 4122 form; reject non-hyphenated 32-hex strings and malformed values.

- Renderer presets (Step 4)
  - Introduce opt-in renderer presets to control output size and strictness without changing existing defaults.
  - Presets:
    - `classic` (default behavior): mirrors historical defaults.
    - `minimal` (opt-in): generates required-only properties/parameters and applies smaller caps (e.g., strings/arrays/bytes) for concise examples.
  - API: `Renderer.default(preset=None|"classic"|"minimal")` or pass the returned options to `render`/`render_all` via the existing `opt` parameter. Default behavior remains unchanged unless a preset is explicitly selected.

### 0.8.39

- Fix the issue that case insensitive keys in headers not working

### 0.8.38

- Allow to access headers with case insensitive keys
- Drop support to py3.3 because of Tornado

### 0.8.37

- Fix loading error on 'yaml' document
- Fix parameter renderer failed on int/number without 'format'
- Windows Support

### 0.8.33

- Support customized headers when making requests

### 0.8.17

- (not support anymore) implicit dereferencing, which is conflict with 'relative file reference'
  ```json
  "definitions":{
    "User":{
    },
    "AuthorizedUser":{
      "$ref": "User"   --> deferenced to "#/definitions/User"
    }
  }
  ```
- __NEW__ relative file reference
  ```
  "definitions":{
    "User": {
      "$ref": "other_folder/User.json"
    }
  }
  ```
- __NEW__ the root object of external documents can be any object (need to be an Swagger/PathItem object before this version)
- fix issue: use 'netloc' only when no host provided.
