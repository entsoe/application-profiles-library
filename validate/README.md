# Validating CGMES/NCP Shapes

Task: [application-profiles-library#74](https://github.com/entsoe/application-profiles-library/issues/74)

The goal is to validate SHACL before publication.

## Makefile

We run `make` using a [Makefile](Makefile) with the following targets:
- `make zip`: Put all SHACL in `entsoe-SHACL.zip` (this zip is in `.gitignore` so it's not committed)
- TODO `make load`: Load to GraphDB repository https://cim.ontotext.com/graphdb/sparql?repositoryId=cim-shacl . 
  It has public read access.
  The quueries below are run against it, unless metioned otherwise
- `make rdf-validate`: syntax validation, using jena `riot`
- `make sparql-validate`: SPARQL validation, using jena `qparse`

## SPARQL Validation

The plan is to:
- Extract prefix declarations from `cim:`
- Extract all `sh:select` strings
- For each one: prepend the prefixes, then validate eg with jena `qparse`

### Extract Prefixes
First we collect all declared prefixes.
There are [duplicate PrefixDeclarations #81](https://github.com/entsoe/application-profiles-library/issues/81) so we use `distinct`:
```sparql
PREFIX sh: <http://www.w3.org/ns/shacl#>
PREFIX cim1: <http://iec.ch/TC57/CIM100#>
PREFIX cim:  <https://cim.ucaiug.io/ns#>
select distinct * {
  {cim: sh:declare [sh:prefix ?p; sh:namespace ?n]} union
  {cim1: sh:declare [sh:prefix ?p; sh:namespace ?n]}
} order by ?p
```
I extract to CSV and then convert to `prefixes.rq` (form for SPARQL)

There is namespace version conflict for `cim:` and `eu:` due to [Discrepant cim: namespaces between CGMES and NCP #8](https://github.com/entsoe/application-profiles-library/issues/8).
But we pick the newest version since to check a query, these prefixes need to be defined, no matter which precise namespace they use.

### Extract SPARQL

ENTSO-E uses 266 SPARQL queries:
- 247 `PropertyShapes` with `SPARQLConstraint` and link `sh:sparql`
- 19 `NodeShapes` with `SPARQLTarget` ans link `sh:target`. 
  More shapes should use the "trick" of a complex `SPARQLTarget` that doesn't just return candidates to check, but only violations.

We get the shapes, descriptions and SPARQL text with [shacl-sparql.rq](shacl-sparql.rq), and save to [shacl-sparql.csv](shacl-sparql.csv):
```sparql
PREFIX afn: <http://jena.apache.org/ARQ/function#>
PREFIX sh: <http://www.w3.org/ns/shacl#>
select ?shape ?shapeLocalname ?descr ?sparql {
  ?x sh:select ?sparql.
  ?shape sh:sparql|sh:target ?x.
  ?shape sh:property?/sh:description ?descr
  bind(afn:localname(?shape) as ?shapeLocalname)
}
```

### Check SPARQL Composition
One shape gets two descriptions in this way:
```
csvtk cut -f shape shacl-sparql.csv |sort|uniq -d
http://iec.ch/TC57/ns/CIM/Equipment-EU/constraints/IEC61970-600/notSolved/3.0#BoundaryPoint
```
The reason is that `eqn600:BoundaryPoint` has both `sh:target`, and two property shapes `eqn600:BoundaryPoint-bppl1Bppl2, eqn600:BoundaryPoint-bppl3`.
This is benign and I haven't investigated further.

However, 3 more shapes have duplicate localname, and are indeed duplicates (https://github.com/entsoe/application-profiles-library/issues/83) :
```
csvtk cut -f shapeLocalname shacl-sparql.csv |sort|uniq -d
BoundaryPoint
DanglingReferences
IdentifiedObject.description-stringLength
IdentifiedObject.name-stringLength
```

All descriptions are single-line: if we add this filter to the query above, we find nothing:
```sparql
filter(regex(?descr,"\n"))
```

### Extract SPARQL Files

After the above checks, we are ready to write a simple script [shacl-sparql.pl](shacl-sparql.pl) to:
- Iterate each line of [shacl-sparql.csv](shacl-sparql.csv) 
- Make a file `shacl-sparql/<shapeLocalname>.rq`
  - Don't worry about the 3 duplicates above: the result is 263 files not 266
- Compose the file as follows:
```
# <shape>
# <shapeLocalname>
# <descr>

<insert prefixes.rq literally>

<sparql>
```
These queries can be tested one by one for speed and correctness, and one can ruminate whether the query implements the constraint (description)

### Invalid SPARQL

`make sparql-validate` uses `qparse` to parse all extracted SPARQL.
To my pleasant surprise, it found only one error:
```
== shacl-sparql/PowerFlowResult-topologicalNode.rq ==
Lexical error at line 29, column 43.  Encountered: '32' (32), after prefix "PowerFlowResult.valueA"
```

But these report and fix a trailing HAVING without GROUP, which anyone would think is an error:
- https://github.com/entsoe/application-profiles-library/issues/70
- https://github.com/entsoe/application-profiles-library/pull/82

Maybe I need `qparse --strict`? Still thinks it's valid.

Furthermore, rdf4j (GraphDB) reports error `variable 'this' in projection not present in GROUP BY.`

Oh my, we need to pick a validator.


### SPARQL Stats

The script also writes out [shacl-sparql-stats.tsv](shacl-sparql-stats.tsv) with name, chars, lines​ of the SPARQL text.

Descriptive statistics (267 SPARQL queries)

| Metric | Min | Median |  Mean |  Max | Total   |
|--------|-----|--------|-------|------|---------|
| chars  | 104 |    312 | 532.9 | 2833 | 142,273 |
| lines  |   6 |      8 |  11.6 |   63 | 3,089   |

Distributions are right-skewed — mean well above median for both, so a handful of large queries pull the average up while most are compact (~312 chars / 8 lines).

5 most complex queries (by chars)

| name                                   | chars | lines |
|----------------------------------------|-------|-------|
| BoundaryPoint-bppl3                    |  2833 |    63 |
| Switch-connection                      |  2370 |    36 |
| RegulatingControl-point                |  2329 |    17 |
| ReactiveCapabilityCurve-reactiveCountP |  2324 |    39 |
| PowerShiftKeySchedule-associations     |  2226 |    26 |

Note `RegulatingControl-point` is high on chars but only 17 lines (long lines), 
whereas `BoundaryPoint-bppl3` is the clear outlier on both dimensions.

### Complex SPARQLs
All SPARQL queries with >=12 lines (86 rows, sorted by lines desc):

| name                                                                     | chars | lines |
|--------------------------------------------------------------------------|-------|-------|
| BoundaryPoint-bppl3                                                      |  2833 |    63 |
| ReactiveCapabilityCurve-reactiveCountP                                   |  2324 |    39 |
| Terminal.phases-consistencyConnectivityNode                              |  1904 |    38 |
| Model-angleReference                                                     |  1661 |    38 |
| TurbineGovernorDynamics-mbaseEquation                                    |  1973 |    36 |
| Switch-connection                                                        |  2370 |    36 |
| Terminal.phases-consistencyTopologicalNode                               |  1604 |    31 |
| SvPowerFlow.p-synchronousMachine                                         |  1667 |    30 |
| PowerTransformerEnd.ratedU-valueRange                                    |  1382 |    29 |
| CurveData-reactive                                                       |  1290 |    29 |
| CurveData.xvalue-value                                                   |  1587 |    28 |
| SynchronousMachine-reactiveLimits                                        |  1353 |    26 |
| SvVoltage.v-absoluteLimit                                                |  1796 |    26 |
| PowerTransformerEnd.ratedS-valueRange2winding                            |  1026 |    26 |
| PowerShiftKeySchedule-associations                                       |  2226 |    26 |
| SvVoltage.v-limits                                                       |  1652 |    25 |
| SvPowerFlow.q-synchronousMachine                                         |  1354 |    25 |
| GeneratingUnit-typeDependency                                            |  2091 |    25 |
| TransformerEnd.endNumber-unique                                          |   943 |    24 |
| PowerTransformerEnd.x-value                                              |  1242 |    24 |
| AsynchronousMachine-aggregate                                            |  1123 |    24 |
| SynchronousMachine-aggregate                                             |  1057 |    23 |
| ShuntCompensator.sections-valueNonLinear                                 |   938 |    23 |
| ReactiveCapabilityCurve-xvalue                                           |   547 |    23 |
| LoadStatic.staticLoadModelType-zIP2                                      |  1277 |    22 |
| LoadStatic.staticLoadModelType-zIP1                                      |  1275 |    22 |
| LoadStatic.staticLoadModelType-exponental                                |  1294 |    22 |
| LoadStatic.staticLoadModelType-constantZ                                 |  1226 |    22 |
| CsConverter.targetAlpha-applicability                                    |  1213 |    22 |
| RotatingMachine-pAndQcapabilityCurveQ                                    |   792 |    21 |
| LoadResponseCharacteristic.exponentModel-exponentCoefficient             |  1445 |    21 |
| CsConverter.targetGamma-applicability                                    |  1201 |    21 |
| Substation-count                                                         |   490 |    20 |
| RotatingMachine-pAndQcapabilityCurveP                                    |   736 |    20 |
| GeneratingUnit.maxOperatingP-ratedS                                      |   597 |    20 |
| RegulatingControl-samePoint                                              |   622 |    19 |
| DanglingReferences                                                       |   500 |    19 |
| DanglingReferences                                                       |   500 |    19 |
| ControlArea-netInterchangeCalculation                                    |   728 |    18 |
| BoundaryPoint.isExcludedFromAreaInterchange-requiredTieFlow              |  1315 |    18 |
| conformsTo-NC-cardinality                                                |  1237 |    17 |
| Switch-sameTopologicalNode                                               |   857 |    17 |
| RegulatingControl-point                                                  |  2329 |    17 |
| GeneratingUnit-singleActivePowerSlack                                    |   628 |    17 |
| BoundaryPoint-bppl1Bppl2                                                 |   831 |    17 |
| RegulatingControl.targetValue-tapChanger                                 |  1236 |    16 |
| PowerBidScheduleTimePoint-attributes                                     |   751 |    16 |
| ShuntCompensator.maximumSections-numberOfInstances                       |   495 |    15 |
| Terminal.phases-consistencyEquipment                                     |   839 |    14 |
| SvTapStep.position-value                                                 |   757 |    14 |
| SvShuntCompensatorSections.sections-value                                |   816 |    14 |
| PowerTransformerEnd-secondWindingValues                                  |   637 |    14 |
| OperationalLimitSet-limits                                               |  1006 |    14 |
| Measurement.Terminal-requiredCases                                       |  1144 |    14 |
| DiagramObject.IdentifiedObject-DLvalueType                               |   514 |    14 |
| ACLineSegment-BaseVoltageDiff                                            |   676 |    14 |
| usedSettings-NC-cardinality                                              |   312 |    13 |
| spatial-NC-cardinality                                                   |   992 |    13 |
| requires-NC-cardinality                                                  |   993 |    13 |
| keyword-NC-cardinality                                                   |   993 |    13 |
| issued-NC-cardinality                                                    |   993 |    13 |
| accrualPeriodicity-NC-cardinality                                        |   411 |    13 |
| accessRights-NC-cardinality                                              |   993 |    13 |
| Terminal-connection                                                      |   436 |    13 |
| Terminal-EXCH8TopologicalNode                                            |   634 |    13 |
| TapChanger.step-value                                                    |   673 |    13 |
| SynchronousMachineTimeConstantReactance-modelType-SubtransientRoundRotor |   889 |    13 |
| ShuntCompensator.sections-value                                          |   682 |    13 |
| RotatingMachine.q-limits                                                 |   755 |    13 |
| MutualCoupling-terminalsAssignment                                       |   719 |    13 |
| LimitKind.patl-numberOfLimitType                                         |   547 |    13 |
| CurveData-equationY2                                                     |   707 |    13 |
| ACLineSegment-baseVoltage                                                |   728 |    13 |
| SvTapStep.position-SV__4                                                 |   997 |    12 |
| SvTapStep-SV__4                                                          |  1352 |    12 |
| SvSwitch-SV__4                                                           |   730 |    12 |
| SvStatus-SV__4                                                           |   753 |    12 |
| SvShuntCompensatorSections.sections-SV__4                                |   872 |    12 |
| SvPowerFlow-instance                                                     |   860 |    12 |
| StaticVarCompensator-controlMode                                         |   764 |    12 |
| RotatingMachine.p-limits                                                 |   643 |    12 |
| PowerBidDependency.kind-exclusive                                        |   495 |    12 |
| GeneratingUnit.nominalP-valueRangePair                                   |   594 |    12 |
| CurveData-equationY1                                                     |   632 |    12 |
| ConductingEquipment.BaseVoltage-usage                                    |   693 |    12 |


## Other Ideas
- SHACL-SHACL validation:
  - See [Check for Syntax Errors Using SHACL SHACL](https://github.com/Sveino/Inst4CIM-KG/tree/develop/shacl-improved#check-for-syntax-errors-using-shacl-shacl)
  - [application-profiles-library#61](https://github.com/entsoe/application-profiles-library/issues/61) does it with ITB Validate, but other approaches are possible
- [Check for Internal Consistency](https://github.com/Sveino/Inst4CIM-KG/tree/develop/shacl-improved#check-for-internal-consistency)
  - Each NodeShape Should have a Property
  - All PropertyShapes Should be Used
