# SHACL Regression Suite

Home of the reproducible checks asked for in
[#155 add SHACL regression tests](https://github.com/entsoe/application-profiles-library/issues/155).

Every issue labelled
[regressionTest](https://github.com/entsoe/application-profiles-library/issues?q=label%3AregressionTest)
should end up here as a test that fails on the defect and passes on the fix, so
that the defect cannot come back unnoticed.

## Running

```sh
cd validate
pip install -r regression/requirements.txt   # rdflib and pyshacl, once
make regression
```

or, without `make`:

```sh
cd validate
python -m unittest discover -s regression -t regression -v
```

Tests skip themselves when a dependency is missing, so the pure file-format
checks still run on a bare Python. The whole suite takes about 30 seconds, most
of it parsing 106 SHACL files and 30 RDFS vocabularies once.

The suite also runs in CI on every push and pull request, see
[regression.yml](../../.github/workflows/regression.yml).

## Known defects, and how a red test stays useful

42 tests: 29 green guards and 13 that reproduce a defect the SHACL still has.

A test for a live defect is marked `@unittest.expectedFailure` and carries a
`KNOWN DEFECT` paragraph naming the issue and the current count. That keeps the
suite green while the defect is open, and the moment somebody fixes it unittest
reports an **unexpected success** and the run fails, telling you to delete the
decorator. So a fix can never silently leave a stale test behind.

The counts in each docstring are what the check reports against this commit.
When you fix part of a defect, update the count in the same commit.

## What is here

| File | Covers | Green | Known defects |
|------|--------|------:|---------------|
| [test_issue_108_tabs.py](test_issue_108_tabs.py) | `Makefile` recipes and `*.tsv` keep their significant TABs | 5 | -- |
| [test_issue_069_tabs_in_ttl.py](test_issue_069_tabs_in_ttl.py) | the reverse: no TAB anywhere in a `.ttl` | 1 | 1 |
| [test_issue_081_prefix_declarations.py](test_issue_081_prefix_declarations.py) | one namespace per prefix, no duplicate `sh:declare` | -- | 2 |
| [test_issue_083_shape_localnames.py](test_issue_083_shape_localnames.py) | shapes that collide on extraction to `.rq` | -- | 1 |
| [test_issue_153_single_sh_path.py](test_issue_153_single_sh_path.py) | at most one `sh:path` per property shape | 1 | 1 |
| [test_issue_154_allowed_properties.py](test_issue_154_allowed_properties.py) | no property listed twice in one shape | -- | 1 |
| [test_shacl_syntax.py](test_shacl_syntax.py) | Turtle parses, SPARQL parses, no BOM | 4 | -- |
| [test_shacl_wellformedness.py](test_shacl_wellformedness.py) | SHACL-SHACL style checks: contradictions, unknown `sh:` terms | 8 | 2 |
| [test_sparql_antipatterns.py](test_sparql_antipatterns.py) | `$this`, `HAVING`, boolean handling inside `sh:select` | 3 | 1 |
| [test_profile_agreement.py](test_profile_agreement.py) | shapes only mention terms the RDFS declares | -- | 3 |
| [test_internal_consistency.py](test_internal_consistency.py) | no vacuous shape, no unreferenced shape | 1 | 1 |
| [test_validation_fixtures.py](test_validation_fixtures.py) | pySHACL golden fixtures under [fixtures/](fixtures) | 2 | -- |
| [test_release_packaging.py](test_release_packaging.py) | every SHACL file is inside the packaging globs | 4 | -- |
| [helpers.py](helpers.py) | shared fixtures: file discovery, LF-normalised reads, cached graphs | | |

### The 13 known defects

| Check | Count today | Issue |
|-------|------------:|-------|
| TAB inside a `.ttl` | 11 lines in 6 files | [#69](https://github.com/entsoe/application-profiles-library/issues/69) |
| prefix bound to more than one namespace | 2 | [#81](https://github.com/entsoe/application-profiles-library/issues/81), [#8](https://github.com/entsoe/application-profiles-library/issues/8) |
| the same prefix declared twice on one subject | 5 | [#81](https://github.com/entsoe/application-profiles-library/issues/81) |
| shapes sharing a local name | 2 names, 5 shapes | [#83](https://github.com/entsoe/application-profiles-library/issues/83) |
| property shape with two `sh:path` values | 8 | [#153](https://github.com/entsoe/application-profiles-library/issues/153) |
| `*-AllowedProperties` listing a property twice | 948 in 3 files | [#154](https://github.com/entsoe/application-profiles-library/issues/154) |
| `BIND(EXISTS{...})` used only as a filter | 49 | [#141](https://github.com/entsoe/application-profiles-library/issues/141) |
| **`sh:` terms SHACL does not define** | 2 | *no issue yet* |
| **`sh:group` pointing at an undeclared group** | 1 | *no issue yet* |
| **`sh:path` no profile declares** | 1 | *no issue yet* |
| **`sh:targetClass` no profile declares** | 52 distinct, 372 uses | *no issue yet* |
| **`sh:class` no profile declares** | 3 | *no issue yet* |
| **NodeShape that constrains nothing** | 1 | *no issue yet* |

The six in bold were found by writing these tests and have no issue yet. The
sharpest of them are silent: a misspelled SHACL term and a `sh:targetClass` that
matches no class both make a constraint disappear without any engine complaining.
Details, including the suggested spellings, are in the docstring of each test.

## Adding a test

1. Name the file after the issue: `test_issue_<nnn>_<slug>.py`, or after the
   subject if there is no issue.
2. Put the issue link and a short description of the *defect* in the module
   docstring -- the next reader needs to know what a failure means.
3. Assert on the whole offender list, not on the first offender.
   `helpers.offenders_message()` formats one.
4. Read files through `helpers.read_text()`. Windows checkouts use
   `core.autocrlf=true`, so the working tree holds CRLF while the committed blob
   holds LF; a test must not care which one it is looking at.
5. Break the thing on purpose and confirm the test fails with a message you
   would want to receive. `@unittest.expectedFailure` also swallows exceptions,
   so a test that crashes looks exactly like a test that reproduces a defect --
   check the message, not just the colour.

### Per-file or merged graph?

`helpers` offers both, and they find different defects. The two are not
interchangeable, and each has a worked example in this suite:

- `graph_of(path)` -- one file. [#154](test_issue_154_allowed_properties.py) is
  a repeated statement inside a single file. Counting it in the merged graph
  would also flag every shape IRI that two files legitimately contribute to.
- `merged_graph()` -- all 106 SHACL files at once, which is how they ship in
  `entsoe-SHACL.zip` and how an engine loads them.
  [#153](test_issue_153_single_sh_path.py) is invisible per file: each file
  contributes one `sh:path`, in its own `cim:` namespace variant.

Blank nodes never leak between files -- rdflib mints fresh ids per parse.

## Golden fixtures

[fixtures/](fixtures) holds the only tests that *run* the shapes rather than
read them. A constraint can parse cleanly, reference only declared terms, pass
every check above, and still validate the wrong thing. Each fixture pairs data
that must pass with data that must fail, and pins the exact validation results:

    fixtures/<name>/
        shapes.txt      repo-relative SHACL files to load, one per line
        conforming.ttl  must produce no results at all
        violating.ttl   must produce exactly the results in expected.txt
        expected.txt    <focusNode> <sourceShape> <severity>, one per line

Both directions matter: `conforming.ttl` catches a constraint that has become
too strict, `violating.ttl` one that has gone slack. The two shipped fixtures
cover a cardinality shape and a SPARQL shape; see the docstring in
[test_validation_fixtures.py](test_validation_fixtures.py) for how to add more.

## Backlog

Ideas not yet implemented, roughly by value:

- **A fixture per SPARQL constraint.** 248 `sh:select` constraints carry most of
  the semantics and all of the complexity, and two of them are covered. This is
  the highest-value work left, and it is incremental -- one directory per
  constraint, added whenever somebody touches that constraint.
- **Shape coverage of the profiles.** The reverse of
  [test_profile_agreement.py](test_profile_agreement.py): every class in a
  profile should have a shape, and every `*-AllowedProperties` shape should list
  exactly that class's profile properties, none missing and none extra. This is
  where authoring defects such as
  [#126](https://github.com/entsoe/application-profiles-library/issues/126) hide.
- **Per-profile term scoping.** `test_profile_agreement.py` checks `sh:path` and
  `sh:targetClass` against the union of all RDFS vocabularies. Checking each
  SHACL file against *its own* profile would also catch a shape that references
  a term belonging to a different profile.
- **`?v = true` comparisons.** The typed-literal half of
  [#141](https://github.com/entsoe/application-profiles-library/issues/141) is
  clean, but plain `FILTER(?indur = true)` remains and is still just `?indur`.
  Not currently counted, because unlike the typed literal it is a readability
  call rather than a defect.
- **`sh:order` uniqueness within an `sh:group`**, so report ordering is stable.
- **Ontology metadata consistency**: `owl:versionIRI`, `owl:versionInfo` and
  `dcterms:identifier` agreeing with the file name and with each other.
- **A second engine.** Everything here runs on rdflib and pySHACL. Jena and
  rdf4j already disagree about `HAVING` without `GROUP BY`
  ([#70](https://github.com/entsoe/application-profiles-library/issues/70));
  running the fixtures on a second engine would turn that class of disagreement
  into a test result instead of a footnote in `validate/README.md`.
