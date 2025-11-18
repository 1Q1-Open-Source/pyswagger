## Changes

### Unreleased

- Flask test client: preserve multi-value response headers
  - When a Flask response includes repeated headers with the same name (e.g., `Set-Cookie`, `Link`), the client now forwards all occurrences to the core Response object instead of collapsing/overwriting them.
  - Response.header continues to expose values as lists (existing API), e.g., `resp.header['X-Thing'] == ['a','b']`. Single headers remain single-item lists for backward compatibility.
  - Case-insensitive header aggregation is improved to ensure mixed-case duplicates (e.g., `link` and `Link`) are combined.

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
