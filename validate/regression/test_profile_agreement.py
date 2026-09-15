"""Do the shapes talk about terms the profiles actually define?

A shape whose `sh:targetClass` names a class no profile declares never matches
anything, so it reports conformance forever. A shape whose `sh:path` names a
property no profile declares can never be violated either. Neither shows up in a
syntax check, in SHACL-SHACL, or in a validation run against clean data -- the
shape simply sits there looking like coverage it does not provide.

The reference is the union of the shipped vocabularies, `CGMES/RDFS/*.rdf` and
`NCP/RDFS/*.rdf`: 30 files, 1249 classes, 5822 properties.

Only IRIs in the CIM and NC namespaces are checked. Terms from `rdf:`, `prov:`,
`dcat:` and friends are external vocabularies that the RDFS files are not
expected to redeclare, and `sh:path rdf:type` is legitimate SHACL.
"""

import unittest

from helpers import (
    SH,
    local_name,
    merged_graph,
    offenders_message,
    rdfs_files,
    require_rdflib,
    vocabulary_terms,
)

# Namespaces the shipped RDFS is responsible for.
CIM_NAMESPACES = (
    "http://iec.ch/TC57/",
    "https://cim.ucaiug.io/",
    "https://cim4.eu/",
)


def suggest(iri, candidates, cutoff=0.8):
    """Nearest declared term, to tell a typo apart from a genuinely missing one."""
    import difflib

    namespace = str(iri).rsplit("#", 1)[0] + "#"
    pool = [
        local_name(c) for c in candidates if str(c).startswith(namespace)
    ]
    match = difflib.get_close_matches(local_name(iri), pool, 1, cutoff)
    return "  (did you mean %s?)" % match[0] if match else ""


class ProfileAgreementTest(unittest.TestCase):
    def setUp(self):
        require_rdflib()
        self.assertNotEqual([], rdfs_files(), "no RDFS vocabularies found")
        self.declared = vocabulary_terms()

    def undeclared(self, predicate):
        from rdflib import URIRef

        used = {
            str(o)
            for o in merged_graph().objects(None, URIRef(SH + predicate))
            if isinstance(o, URIRef)
        }
        in_scope = {u for u in used if u.startswith(CIM_NAMESPACES)}
        return sorted(in_scope - self.declared), len(in_scope)

    def check(self, predicate, explanation):
        offenders, total = self.undeclared(predicate)
        self.assertEqual(
            [],
            offenders,
            offenders_message(
                "%s -- %d of %d sh:%s values in CIM/NC namespaces"
                % (explanation, len(offenders), total, predicate),
                offenders,
                render=lambda o: o + suggest(o, self.declared),
            ),
        )

    @unittest.expectedFailure
    def test_every_sh_path_is_a_declared_property(self):
        """KNOWN DEFECT: 1 of 5111.

        `cim:AccumulatorValue.value` -- the class `cim:AccumulatorValue` is
        declared, the property is not.
        """
        self.check("path", "sh:path values no profile declares")

    @unittest.expectedFailure
    def test_every_sh_target_class_is_a_declared_class(self):
        """KNOWN DEFECT: 52 of 914, used 372 times.

        51 of them are in the legacy CIM16 namespace
        `http://iec.ch/TC57/2013/CIM-schema-cim16#`, concentrated in three NCP
        files: EquipmentReliability-AP-Con-Simple (190 uses),
        GridDisturbance-AP-Con-Simple (90) and
        SteadyStateInstruction-AP-Con-Simple (90). The 52nd is
        `cim:GovHydroIEEE1`, where the RDFS declares GovHydroIEEE0 and
        GovHydroIEEE2 but no GovHydroIEEE1.

        Every one of these shapes currently targets a class that no shipped
        profile defines, so none of them can ever match an instance.
        """
        self.check("targetClass", "sh:targetClass values no profile declares")

    @unittest.expectedFailure
    def test_every_sh_class_is_a_declared_class(self):
        """KNOWN DEFECT: 3 of 252, and all three look like spelling mistakes.

        * `cim:CSConverter` -- the profile declares `cim:CsConverter`
        * `nc:AvailablityPlanVersion` -- the profile declares `nc:AvailablityPlan`
        * `nc:OutageRequestVersion` -- the profile declares `nc:OutageRequest`

        A `sh:class` naming an undeclared class can never be satisfied, so any
        instance reaching this constraint is reported as violating.
        """
        self.check("class", "sh:class values no profile declares")


if __name__ == "__main__":
    unittest.main()
