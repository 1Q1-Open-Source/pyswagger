# Step 4 - Defaults and rendering improvements (renderer options)

Date: 2025-11-18 13:20 (local)

This document captures only the fourth step from the initial porting plan: reviewing and improving Renderer defaults in a backward-compatible way.

## Objectives
- Evaluate current Renderer default options and consider safer/minimal defaults inspired by fork changes (e.g., benkilimnik/develop).
- Introduce an opt-in preset for conservative/minimal rendering without changing existing default behavior.
- Keep the API surface stable; any behavior changes must be guarded behind explicit options.

## Scope
- In scope: pyswagger.primitives.Renderer defaults and their effect on generated request/response examples.
- Out of scope: codecs/MIME types, UUID handling, client header behavior, CI/deps, URL parsing changes (covered in other steps).

## A) Analyze current defaults and choose strategy
1) Inventory current defaults from Renderer.default():
   - max_name_length, max_prop_count, max_str_length, max_byte_length, max_array_length, max_file_length
   - minimal_property, minimal_parameter (both False)
   - files, object_template, parameter_template
   - max_property, max_parameter (both False)
2) Compare with fork deltas; identify safer values that reduce output size and noise, and improve test speed.
3) Decision: keep legacy defaults as the global default and add a "minimal/safe" preset that users can opt into. Document potential future flip after a deprecation window.

### Sources to reuse
- benkilimnik/develop: commit `b73b1d8` adjusted renderer defaults; reuse those values as inspiration for the new opt-in "minimal" preset (do not change current defaults).
- Note: commit `1bd938f` (URL parsing) exists in the same fork but is out of scope for this step.

## B) Presets and option guarding (design only in this step)
- Add named presets (non-breaking):
  - "classic" (current behavior) - mirrors existing defaults exactly.
  - "minimal" (new) - emphasizes required-only, smaller outputs.
- Proposed minimal preset values (to finalize during implementation):
  - minimal_property = True
  - minimal_parameter = True
  - Moderately lower caps for max_prop_count, max_array_length, max_str_length (exact values to be validated by tests).
- API ideas (no signature change):
  - Allow Renderer.default(preset="classic"|"minimal") or expose Renderer.presets["minimal"].
  - Continue passing presets via the existing opt parameter to render/render_all.
- Backward compatibility:
  - Default behavior remains unchanged unless the new preset is explicitly used.
  - If future work flips the default, deprecate the old default with a clear CHANGES.md note and a one-release deprecation window.

## C) Behavioral rules to confirm
- When minimal flags are True: only required properties/parameters are generated unless templates override.
- Bounds respected: arrays/strings/bytes never exceed max_*; file generator obeys max_file_length.
- Determinism guidance: document how to seed randomness in tests (recommend users call random.seed(...) as needed) without changing library defaults.

## D) Tests to add/update
- Minimal preset enforces required-only:
  - Schema with required + optional: minimal omits optionals; classic may include them subject to randomness.
- Bounds respected under minimal caps.
- Parameter omission in render_all with minimal preset for optional params.
- Template overrides still apply under minimal preset.
- Non-regression: classic behavior unchanged; existing tests pass without modification.

## E) Documentation updates
- Update docs/md/tutorial/render.md to describe presets (classic vs minimal), selection, and examples.
- Add Unreleased entry in CHANGES.md noting preset introduction and that default behavior is unchanged in this step.

## F) Acceptance criteria
- Minimal preset is available and documented; default behavior remains classic.
- Renderer honors required-only and bounds under minimal preset.
- Existing renderer tests pass; new tests cover minimal preset behavior.
- Docs and CHANGES.md updated.

## G) PR contents (recommended)
- Code: introduce preset mechanism (classic + minimal) without changing defaults.
- Tests: required-only, bounds, parameter omission, template override, non-regression for classic.
- Docs: tutorial/render.md updates; CHANGES.md Unreleased entry.

## Developer checklist (Step 4)
- [ ] Review fork deltas; finalize preset strategy
- [ ] Implement preset support (classic + minimal)
- [ ] Enforce bounds and required-only in minimal preset
- [ ] Add tests listed above
- [ ] Update docs and CHANGES.md
- [ ] Run test suite on supported Python versions

## Risks and mitigations
- Risk: Changing defaults breaks consumers.
  - Mitigation: Keep classic as default; minimal is opt-in; document potential future change with deprecation notice.
- Risk: Presets complicate API.
  - Mitigation: Implement via options dicts without altering method signatures; provide clear docs.

## Definition of done for Step 4
- Renderer exposes an opt-in minimal preset; classic default unchanged.
- Tests demonstrate minimal preset correctness and preserve classic behavior.
- Documentation and changelog updated.

---