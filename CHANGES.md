## Changes

### Unreleased

#### Added
- (placeholder)

#### Changed
- (placeholder)

#### Fixed
- (placeholder)

#### Removed/Deprecated
- (placeholder)

#### Migration notes
- (placeholder)

### 0.9.0 — 2025-12-01

#### Added
- GitHub Actions CI workflow to run tests on Python 3.8, 3.10, and 3.12 with pip caching. (Step 5)
- Support for `application/hal+json` via the JSON codec, including parameterized content types like `; charset=utf-8`. (Step 3)
- Renderer presets: opt-in `minimal` preset alongside historical `classic` behavior. (Step 4)
- Targeted tests covering YAML safety, import/ABC compatibility, dynamic import via `utils.import_string`, and ISO-8601 negative cases. (Step 6)

#### Changed
- Flask test client now preserves multi-value response headers, forwarding all occurrences (e.g., `Set-Cookie`, `Link`) to the core Response object. Header aggregation is case-insensitive. (Step 2)
- UUID format handling updated: outbound `uuid.UUID` values are serialized to canonical strings; string validation expects hyphenated RFC 4122 form. (Step 3)
- Documentation and badges updated to reflect Git-based installation and CI status. (Step 7)

#### Fixed
- Legacy tests and imports updated to avoid `imp` and to use `collections.abc` for Python 3.8–3.12 compatibility. (Step 1/5)
- Improved determinism across tests; avoid external network I/O. (Step 6)

#### Removed/Deprecated
- Remove legacy/unmaintained dev dependencies (`pudb`, `webapp2`) from active requirements; legacy webapp2 tests guarded to auto-skip on Python 3. (Step 5)

#### Migration notes
- Flask client multi-value headers: Code that assumed a single string value must handle lists when duplicates are present, e.g., `resp.header['Link']` may be `['<...>; rel="next"', '<...>; rel="prev"']`. Do not join `Set-Cookie` values; handle each cookie separately.
- Renderer presets: Defaults unchanged. To opt into the `minimal` preset, use `Renderer.default('minimal')` and pass the options to `render`/`render_all`.
- HAL codec: `application/hal+json` is supported out of the box; no changes required unless custom workarounds existed.
- UUID format: Outbound `uuid.UUID` values are serialized to strings; inbound values remain strings.
- Python versions: Use Python 3.8–3.12 with updated dependencies from `requirements*.txt`.

#### Version
- Bump version to 0.9.0 and tag release.

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
