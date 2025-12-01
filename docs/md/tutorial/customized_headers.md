## Customized Headers when making requests

Sometimes you need to add customized headers that are not listed in OpenAPI specs,
you can get this done in this way:

```python
from pyswagger import App
from pyswagger.contrib.client.requests import Client

app = App.create('http://petstore.swagger.io/v2/swagger.json')
client = Client()

# provide a header
client.request(
    app.op['getUserByName'](username='Tom'),
    headers={'MY-TEST-HEADER': '123'}
)

# headers with multiple value to one key
client.request(
    app.op['getUserByName'](username='Tom'),
    headers=[('MY-TEST-HEADER', '123'), ('MY-TEST-HEADER', '456')],
)

# headers with multiple value to one key, and join them by comma
client.request(
    app.op['getUserByName'](username='Tom'),
    headers=[('MY-TEST-HEADER', '123'), ('MY-TEST-HEADER', '456')],
    opt={'join_headers': True}
)
```

---

## Accessing response headers (duplicates and case-insensitive keys)

When reading headers from a Response, `resp.header` is a case-insensitive mapping where each value is a list of strings. This preserves duplicates (e.g., `Set-Cookie`, `Link`). Single headers appear as single-item lists for consistency.

Examples:

```python
# Assume you already have (req, resp) and a client
result = client.request((req, resp))

# Case-insensitive access
links = result.header.get('link', [])        # same as result.header.get('Link')

# Duplicates preserved as a list
for link in links:
    process_link_header(link)

# Cookie handling: do NOT join Set-Cookie values
cookies = result.header.get('Set-Cookie', [])
for set_cookie in cookies:
    cookiejar.extract_cookies_from_set_cookie(set_cookie)

# For headers that are known to be single-valued, take the first item if present
content_type = (result.header.get('Content-Type') or [None])[0]
```

Caution:
- Do not join `Set-Cookie` into a single string; each cookie must be handled separately per RFC 6265.
- Header name lookups are case-insensitive.

