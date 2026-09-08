# Conformance test suite for CGMES / NCP profiles — proposal

Source: [Propsal: Add sht:Validate artifacts for conformance suite and clearly document current RDFS, SHACL, PROF scope (#166)](https://github.com/entsoe/application-profiles-library/issues/166), text as of 2026-09-08 (incl. the first-paragraph edit by @VladimirAlexiev). Published here for inline review; the issue stays for discussion of scope. Related: [#43](https://github.com/entsoe/application-profiles-library/issues/43) (business need for a validation setup), [#74](https://github.com/entsoe/application-profiles-library/issues/74) / [`validate/`](../validate) (pre-publication checks of the shape files).

---

## 0. Summary

### Why?

This repo already publishes PROF, RDFS, SHACL. It does not say how a validator should run a profile against instance data (which data graphs to validate against which shapes). Also there are ony positive (green) tests in ReliCapGrid data and no negative cases, thus the Shape Constraints are left without formal check themselves - eg whether they catch their intended errors or not.

This separate issue:
- [#43](https://github.com/entsoe/application-profiles-library/issues/43) 
proposes how to solve it in SHACL and PROV, but looking into how it is solved by W3C, that seems not a good solution anymore  


### Proposed solution

1. Treat RDFS / SHACL / PROF as the normative profile stack (already true).
1. Add a fourth, separate artifact family: a W3C-style test manifest (`mf:Manifest + sht:Validate`) that runs those profiles against ReliCapGrid 
3. Add diff/modification functionality, to test Shapes (SHACL own conformity tests style), and to not recreate erroneous instance data within ReliCapGrid - instead to generate it on the fly

### Useful links

- DAWG manifest vocabulary: `http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#`
- SPARQL test structure (`qt:`, `ut:`): [DAWG test README](https://www.w3.org/2001/sw/DataAccess/tests/README.html), [SPARQL 1.1 tests](https://w3c.github.io/rdf-tests/sparql/sparql11/)
- [SHACL Test Suite and Implementation Report](https://w3c.github.io/data-shapes/data-shapes-test-suite/)
- SHACL 1.2 Core §6.1–6.4 — shapes graph, data graph, `owl:imports`, `sh:shapesGraph`: https://www.w3.org/TR/shacl12-core/
- [The Profiles Vocabulary (dx-prof)](https://www.w3.org/TR/dx-prof-1.0/) — §8–9 roles `vocabulary`, `constraints`, `validation`
- [SHACL 1.2 Profiling](https://www.w3.org/TR/shacl12-profiling/)
- EARL 1.0 Schema — SHACL `reports/` folder on [w3c/data-shapes](https://github.com/w3c/data-shapes/tree/gh-pages/data-shapes-test-suite/reports)
- rdfpytest (discovers `sht:Validate`, allows extra IRIs on the entry): https://github.com/WEHI-SODA-Hub/rdfpytest
- SHACL-DS (dataset validation, not Rec): https://arxiv.org/abs/2505.09198

## 1. Why a separate artifact

Today a tool author has:

| What exists | What it answers |
|---|---|
| RDFS (`*-Voc-RDFS2020`) | Classes, properties, datatypes |
| SHACL Simple / Complex / Validation | Constraints and shape IDs |
| PROF (`prof:Profile` + `prof:hasResource`) | *Which* RDFS and SHACL files belong to profile URI `https://ap.cim4.eu/…` |
| Instance header `dcterms:conformsTo` / `Model.profile` | *Claimed* profile of a dataset |

What is **not** specified:

- Must EQ + SSH + TP be validated as a **union**, as **named graphs**, or one file at a time?
- Does “validate Equipment” mean Simple SHACL only, or Simple+Complex?
- How do we test that a **shape actually fires** (negative case) without copying ReliCapGrid a hundred times?
- How does an engine publish an implementation report?

PROF is a **catalog**. It must not become a test runner. The W3C Profiles Vocabulary is explicit: it describes artifacts and roles; it does not define validation semantics.

---

## 2. Layer stack (who owns what)

```
STATIC (authored once)                         RUNTIME (harness)
─────────────────────                          ─────────────────
1. RDFS vocabulary                             1. Read manifest row
   classes, properties, datatypes              2. Resolve profile → PROF → shapes
        │                                      3. Assemble data graphs (load set)
        ▼ is described by                      4. Optional delta (.ru or DifferenceModel)
2. PROF profile (catalog)                      5. shacl.validate(data, shapes)
   role:vocabulary  → RDFS                     6. Compare to mf:result
   role:constraints → Simple SHACL             7. Emit EARL (not authored)
   role:constraints → Complex SHACL
   role:validation  → Validation SHACL
        │ hasArtifact
        ▼
3. SHACL files (shape IDs live here)
        ▲
        │ cim:profile (resolve; do not restate the file list)
4. mf:Manifest  ← separate artifact
        │
        ▼
5. Test case row
   GREEN:    no delta, assert sh:conforms true
   NEGATIVE: apply delta, assert named shape ID in the report
```

**Doctrine in one line:** PROF = catalog. Manifest = runner. Datatypes = RDFS. Delta lives only on the negative row. EARL is engine output.


### 2.1 Layer details

**Layer 1 - RDFS vocabulary.** Domain model only. Classes, properties, cardinalities, and data types.  (will partially overlap with SHACL, but is desiarable - partially overlapping views of same data)

**Layer 2 - PROF profile.**  Instance data points to PROF, that will then link to RDFS + SHACL “which rules belong to this profile.” 

`prof:hasResource` + `prof:hasRole`:

- `role:vocabulary` → RDFS (including datatypes)
- `role:constraints` → Simple and/or Complex SHACL (partial duplication of RDFS,  but beneficial for cross checking and different tooling)
- `role:validation` → Validation SHACL, when present
- `role:specification` → human document (optional)

**Layer 3 - SHACL rule files.** Actual constraints. Referenced by PROF. Never duplicated as a file list inside the manifest. Each rule that we want to target in a negative test needs a stable shape IRI (`sh:sourceShape`).

**Layer 4 - Manifest (`mf:Manifest`).** Test-suite index. Each entry is `sht:Validate`. The action points at data + shapes (W3C core) and, if we agree, a small CIM/SPARQL extension for multi-file load sets and deltas. The harness **walks PROF from here**; it does not restate the SHACL file list.

**Layer 5 - Test case rows.** 

- **Green path**  no delta. Load the reference data as assembled, validate, assert `sh:conforms true` (or a known partial report).
- **Negative path**  apply one atomic delta, validate, assert the report names a specific shape IRI.

**Outside the chain - EARL report.** 


## 4. Alignment with W3C

Official SHACL test case shape ([SHACL Test Suite](https://w3c.github.io/data-shapes/data-shapes-test-suite/)):

```turtle
<entry1> a sht:Validate ;
   mf:name "…" ;
   mf:action [
        sht:shapesGraph <example-shapes.ttl> ;
        sht:dataGraph   <example-data.ttl> ;
   ] ;
   mf:result [
        a sh:ValidationReport ;
        sh:conforms true ;
   ] ;
   mf:status sht:proposed .
```

Few things to be aware of

### Shapes need to be single entity. (Seen this already been done in PROV - so all good)

W3C composes shapes with owl:imports (or sh:shapesGraph) inside the shapes graph. One wrapper file that imports Simple + Complex is a valid sht:shapesGraph. PROF already lists those files; the wrapper is just PROF flattened. No urgent need for custom extentsion like cimx:shapesGraphs unless we want to remove the imports in PROV.

### Instancae Data needs to be single entity (This is an issue)

sht:dataGraph cannot be a list. EQ + SSH + TP therefore need either a compiled union file (vanilla sht:dataGraph) or an extension list (cimx:dataGraphs).

### Invalid data generation (Needs probably the longest discussion)

sht: has no edit step. Possible options:

ut:request → .ru is the W3C way to write “apply this change.” The row stays sht:Validate. 

A DifferenceModel file is the CIM-native twin of the same idea, but would require custom extension like cimx:applyDiff

### Report format
EARL is how an engine reports the suite.


## 5. Worked examples

Prefixes used below:

```turtle
@prefix mf:   <http://www.w3.org/2001/sw/DataAccess/tests/test-manifest#> .
@prefix sht:  <http://www.w3.org/ns/shacl-test#> .
@prefix sh:   <http://www.w3.org/ns/shacl#> .
@prefix ut:   <http://www.w3.org/2009/sparql/tests/test-update#> .
@prefix prof: <http://www.w3.org/ns/dx/prof/> .
@prefix role: <http://www.w3.org/ns/dx/prof/role/> .
@prefix cimx: <https://ap.cim4.eu/test#> .    # proposed local extension ns — name TBD
```

### 5.1 PROF stays a catalog (already APL practice)

```turtle
<https://ap.cim4.eu/Equipment>
  a prof:Profile ;
  prof:hasResource
    [ prof:hasRole role:vocabulary ;
      prof:hasArtifact <61970-600-2_Equipment-AP-Voc-RDFS2020.rdf> ] ,
    [ prof:hasRole role:constraints ;
      prof:hasArtifact <61970-600-2_Equipment-AP-Con-Simple-SHACL.ttl> ] ,
    [ prof:hasRole role:constraints ;
      prof:hasArtifact <61970-600-2_Equipment-AP-Con-Complex-SHACL.ttl> ] .
```


### 5.2 Green path — ReliCapGrid as-is, vanilla `sht:`

```turtle
<#eq-ssh-green> a sht:Validate ;
  mf:name "ReliCapGrid EQ+SSH conforms to Equipment+SSH profiles" ;
  mf:action [
    sht:dataGraph   <assembled-eq-ssh.trig> ;     # pre-unioned, or <> 
    sht:shapesGraph <eq-ssh-shapes.ttl> ;         # owl:imports Simple+Complex
  ] ;
  mf:result [ a sh:ValidationReport ; sh:conforms true ] ;
  mf:status sht:proposed .
```

Optional sugar on the same row (ignored by a stock walker):

```turtle
  cimx:profile       <https://ap.cim4.eu/Equipment> , <https://ap.cim4.eu/SteadyStateHypothesis> ;
  cimx:dataGraphs    ( <relicap/eq.xml> <relicap/ssh.xml> ) ;
  cimx:boundaryGraph <relicap/eq-bd.xml> .
```

### 5.3 Negative path — SPARQL Update as the delta (`ut:request`)

`tests/drop-conducting-equipment.ru`:

```sparql
PREFIX cim: <http://iec.ch/TC57/CIM#>

DELETE DATA {
  <urn:uuid:terminal-1> cim:Terminal.ConductingEquipment <urn:uuid:breaker-1> .
}
```

Manifest row:

```turtle
<#term-orphan> a sht:Validate ;
  mf:name "Orphan Terminal fires TerminalMustHaveEquipment" ;
  mf:action [
    sht:dataGraph   <relicap/eq.xml> ;
    sht:shapesGraph <eq-shapes.ttl> ;
    ut:request      <drop-conducting-equipment.ru>      # SPARQL Update, W3C syntax
  ] ;
  mf:result [
    a sh:ValidationReport ;
    sh:conforms false ;
    sh:result [ sh:sourceShape <https://ap.cim4.eu/Equipment#TerminalMustHaveEquipment> ]
  ] ;
  mf:status sht:proposed .
```


### 5.4 Negative path — CIMXML DifferenceModel as the delta (`cimx:applyDiff`)

Same intent, domain-native payload (IEC 61970-552 `DifferenceModel` / forward + reverse differences):

```turtle
<#term-orphan-dm> a sht:Validate ;
  mf:action [
    sht:dataGraph    <relicap/eq.xml> ;
    sht:shapesGraph  <eq-shapes.ttl> ;
    cimx:applyDiff   <drop-conducting-equipment.xml>    # CIMXML DifferenceModel
  ] ;
  mf:result [
    a sh:ValidationReport ;
    sh:conforms false ;
    sh:result [ sh:sourceShape <https://ap.cim4.eu/Equipment#TerminalMustHaveEquipment> ]
  ] .
```

### 5.5 Possible folder structure

A minimal tree that already runs on stock tools **and** on an extended harness:

```
conformance/
  README.md
  manifest.ttl                 # mf:Manifest of sht:Validate entries
  shapes/
    eq-ssh-wrapper.ttl         # Optional: owl:imports Simple+Complex from APL (if not reusing new PROV approach)
  delta/
    drop-conducting-equipment.ru
    drop-conducting-equipment.xml   # optional DifferenceModel twin
  compiled/                    # optional, for stock walkers, if we use extentsions, we could compile to native
    term-orphan-data.ttl
  reports/                     # EARL drops from engines
```

## 6. Open points

These are the only places we would extend W3C. Everything else is stock.

### OP-1 — Load set: `cimx:dataGraphs` on the test row **vs** “it is already in PROF / the header”

**Option A — list on the action (proposed default for the runner)**

```turtle
mf:action [
  sht:dataGraph    <assembled.trig> ;          # compiled form
  cimx:dataGraphs  ( <eq.xml> <ssh.xml> <tp.xml> ) ;
  cimx:boundaryGraph <eq-bd.xml> ;
]
```

- Pros: the *test* says exactly which files this case uses; green and negative rows can share one ReliCapGrid copy; matches how SPARQL tests list `qt:graphData`.
- Cons: not in `sht:`; stock walkers ignore the list unless compiled.

**Option B — derive the load set from PROF / `Model.profile` / `DependentOn` as today**

Header already lists profile URIs; CGMES already has `Model.DependentOn` between EQ / SSH / TP / SV.

- Pros: no new property; one source of truth with operational exchange.
- Cons: PROF does not name *instance files*; headers name profiles, not “this test uses *this* ReliCapGrid EQ”. A test suite still needs to point at concrete graphs. Cross-profile Complex SHACL (e.g. NotSolvedMAS) needs an explicit assembly that PROF alone cannot give.

**Proposal to discuss:** PROF remains the catalog of *rules*. The manifest names the *instance graphs* for that row (`cimx:dataGraphs`), and **must** also ship a compiled single `sht:dataGraph` so vanilla tools work. 

### OP-2 — Shapes set: `cimx:shapesGraphs` **vs** PROF + `owl:imports`

**Option A — `cimx:shapesGraphs ( … )` on the action.** Symmetric with data graphs. Risks restating PROF.

**Option B (preferred):** one `sht:shapesGraph` whose file `owl:imports` Simple+Complex (or a tiny wrapper generated from PROF at publish time). Manifest has `cimx:profile` only as sugar: “resolve this PROF URI.”

`sh:shapesGraph` on the *data* is the W3C hook if instance data should suggest its shapes. CGMES headers already point at profile URIs; mapping profile URI → PROF → artifacts is the missing published algorithm, not a new shapes-list property.

### OP-3 — Delta language: `ut:request` (`.ru`) **vs** `cimx:applyDiff` (CIMXML DifferenceModel)

| | `ut:request` + `.ru` | `cimx:applyDiff` + DifferenceModel |
|---|---|---|
| Standard | W3C SPARQL Update | IEC 61970-552 |
| Tooling | Every RDF stack | CIMXML / CGMES tooling |
| Audience | Semantic-web implementers | TSO / IOP / vendor CIM tools |
| Official SHACL suite | Does **not** run `.ru` | Does not know DifferenceModel |
| Applies in memory | Yes (SPARQL Update engine) | Yes (DifferenceModel merge) |
| Can be loaded as extra graph without merge? | No — still must apply | No — still must apply |

**Proposal to discuss:** support **both**, same semantics (base + apply + validate). Prefer `.ru` in the semantic-web conformance slice; prefer DifferenceModel in the CGMES/IOP slice. Do **not** invent a third `cimx:patch` triple vocabulary. Do **not** treat “diff file loaded as named graph” as the mutated model.

`sht:` has **no** edit step. Reusing `mf:UpdateEvaluationTest` as the *test type* is wrong: its oracle is graph-store isomorphism, not a `sh:ValidationReport`. Reuse only the **update document** (`ut:request`).

### OP-4 — Named graphs vs flattened union

SHACL 1.0/1.2 validates **one** data graph. Flattening EQ+SSH+TP is the workaround everyone uses; [SHACL-DS](https://arxiv.org/abs/2505.09198) exists because that loses provenance. SPARQL tests keep graphs named via `qt:graphData`.

For v1 of this suite: **flatten to one data graph** (compiled `sht:dataGraph`), document it, leave SHACL-DS as a later option. Cross-profile rules stay expressible.

### OP-5 — Inference

Official SHACL suite has no per-case `rdfs` flag. If Complex constraints assume RDFS closure, say so **once** at suite or profile level (`cimx:inference` default), do not fork every row.

### OP-6 — Where the suite lives?

maybe new tree in this repo, e.g. `conformance/`, versioned with APL releases.
