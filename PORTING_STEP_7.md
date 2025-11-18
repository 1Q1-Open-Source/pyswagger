
Update the following docs to reflect new capabilities and behaviors:

- README.md
  - Supported Python versions (3.8–3.12) if confirmed.
  - CI badge update to GitHub Actions after Step 5 is merged (keep Travis badge only if still active).
  - Installation section must reflect Git-based installation. Provide examples:
    - `python -m pip install "pyswagger @ git+https://github.com/1Q1-Open-Source/pyswagger.git@v<RELEASE_TAG>"`
    - `python -m pip install git+https://github.com/1Q1-Open-Source/pyswagger.git@<COMMIT_SHA>`
    - `python -m pip install https://github.com/1Q1-Open-Source/pyswagger/archive/refs/tags/v<RELEASE_TAG>.zip`
  - Add a brief mention of HAL support and UUID format handling in Features/Reference areas.

- docs/md/tutorial/customized_headers.md
  - Document header access semantics: single header → str; repeated headers → list[str].
  - Example for Set-Cookie and Link headers; caution against joining Set-Cookie values.

- docs/md/tutorial/mime.md
  - Note support for application/hal+json (and that it behaves like JSON initially).

- docs/md/tutorial/extend_prim.md (or relevant data types reference)
  - Describe format: uuid behavior: accepted values, examples, outbound serialization of uuid.UUID to string, inbound remains string.

- docs/md/tutorial/render.md
  - Introduce presets: classic (current default) vs minimal (opt-in). Show how to select and expected effects (required-only, smaller caps). Include small code snippets.
- docs/md/ref/* (App, client, etc.)
  - If the Flask client response/headers access is documented, update to reflect list[str] for duplicates and case-insensitive behavior.

### Sources to reuse
- Limited direct reuse from forks. Most forks changed or removed docs and targeted PyPI. Use their ideas sparingly (e.g., CI badges), but author documentation tailored to our Git-based installation and chosen semantics.

Notes:
- Keep examples self-contained and runnable where possible.
- Avoid changing API signatures in docs; focus on behavior and usage patterns.

---

## C) Migration guidance

Create or update a migration note to help users adapt:
- Location: a short section in CHANGES.md under Unreleased, and optionally a new file docs/md/migration/next_release.md linked from README.
- Content:
  - Flask client multi-value headers: code that assumed a string should now handle list[str] when duplicates are present; provide a short idiom for normalization, noting not to join Set-Cookie.
  - Renderer presets are opt-in; defaults unchanged. Show how to opt into minimal preset.
  - HAL codec adds new MIME handling; no action required unless users had custom workarounds.
  - UUID format: outbound uuid.UUID are converted to strings; inbound remains strings.
  - Python compatibility: ensure environment uses supported versions and updated dependencies.

---

## D) Versioning plan

- Recommendation: bump a minor version (e.g., from 0.8.x to 0.9.0) because this release adds features (HAL codec, UUID format support) and adjusts observable behavior (multi-value headers), albeit in a compatible way for most consumers.
- If the project follows strict semver and considers header value type changes as a potential break, still treat this as a minor release due to backward-compatible intent and clear documentation; consider a deprecation flag if you provided an opt-out.
- Tasks:
  - Decide target version number with maintainers.
  - Update version metadata in pyswagger/__init__.py (__version__) and setup.py.
  - Update CHANGES.md to add a new version heading, leaving an empty Unreleased section at the top.
  - Ensure README and docs mention the correct version where applicable.
  - Plan for Git tagging and GitHub Release notes (PyPI upload is not in scope).

Note: If you prefer to defer bumping __version__ to Step 9 (Release preparation), retain the finalized version decision here and only update CHANGES.md; perform code metadata bumps in the release PR.

---

## E) Acceptance criteria
- CHANGES.md Unreleased section reflects Steps 1–6, with structured entries and migration notes.
- README and relevant tutorials/references are updated and consistent with implemented behavior.
- A clear version bump decision is recorded; either code metadata is updated here or a note is added to perform it in Step 9.
- All doc links resolve (no broken links) and examples are syntactically correct.
 - README Installation shows Git-based commands and no longer advertises `pip install pyswagger` from PyPI.

---

## F) PR contents (recommended)
- Edits to CHANGES.md with structured Unreleased entries and migration notes.
- README updates (badges, features, supported Python versions).
- Tutorial/reference updates in docs/md (headers, MIME/HAL, UUID, renderer presets).
- Version bump in pyswagger/__init__.py and setup.py (if decided for this step), or a note in the PR description indicating it will occur in Step 9.
- README Installation section updated to Git-based instructions.

---

## Developer checklist (Step 7)
- [ ] Update CHANGES.md with Added/Changed/Fixed/Security/Deprecated/Removed sections covering Steps 1–6
- [ ] Add migration notes (multi-value headers, presets, HAL, UUID, Python compatibility)
- [ ] Update README badges and supported versions (align with CI matrix)
- [ ] Update tutorials: customized_headers.md, mime.md, extend_prim.md (or format ref), render.md
- [ ] Update any reference docs impacted by header behavior or codecs
- [ ] Decide next version number; record decision in PR
- [ ] Update __version__ and setup.py (or defer to Step 9 with a clear note)
- [ ] Validate links/examples; run a quick link check if available

---

## Risks and mitigations
- Risk: Documentation diverges from actual behavior.
  - Mitigation: Cross-check against tests added in Step 6; link to test cases as authoritative examples.
- Risk: Users miss the header behavior change and encounter type errors.
  - Mitigation: Prominent migration note with examples; optionally add an opt-out flag in Step 2 implementation and document it.
- Risk: Premature version bump without all items merged.
  - Mitigation: Perform the doc updates first; bump version only when Steps 1–6 are merged and tests are green.

---

## Definition of done for Step 7
- Documentation accurately reflects all user-visible changes from Steps 1–6.
- Changelog updated with a structured Unreleased entry and migration notes.
- Version bump decision captured; version metadata updated or scheduled for Step 9.
- Docs build (if applicable) completes without warnings; links and examples are valid.

---
