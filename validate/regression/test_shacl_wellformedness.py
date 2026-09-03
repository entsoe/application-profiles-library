"""SHACL-SHACL style checks: shapes that parse but cannot mean what they say.

The kind of defect a Turtle parser is happy with and a validation engine
silently ignores, so it never shows up in a report -- it just quietly stops
constraining anything. See "Check for Syntax Errors Using SHACL SHACL" in
https://github.com/Sveino/Inst4CIM-KG/tree/develop/shacl-improved and issue #61,
which tried the same thing with the ITB validator.

Most of these are green today and are here as guards. The two marked
KNOWN DEFECT are live.
"""

import unittest

from helpers import (
    SH,
    merged_graph,
    offenders_message,
    query,
    rel,
    require_rdflib,
    shacl_files,
    shacl_terms,
)


class VocabularyTest(unittest.TestCase):
    """Terms in the sh: namespace that SHACL does not define.

    The highest-value check here by some distance. A misspelled SHACL term is
    not an error to any engine: it is just an unknown predicate, so the
    constraint is dropped and the shape reports conformance for data it was
    written to reject.

    KNOWN DEFECT: 2 terms.

    * `sh:MinCount 1` on `nc:GenericSequenceSchedule-associations`
      (StateInstructionSchedule-AP-Con-Complex-SHACL.ttl) -- should be
      `sh:minCount`, so no cardinality is enforced at all.
    * `sh:length 16` on `IdentifiedObject.energyIdentCodeEic-stringLength`
      (61970-600-2_IdentifiedObjectCommon_AP-Con-Complex-SHACL.ttl) -- SHACL has
      `sh:minLength` and `sh:maxLength`, there is no `sh:length`, so the EIC
      length is not checked.
    """

    @unittest.expectedFailure
    def test_every_sh_term_used_is_defined_by_shacl(self):
        require_rdflib()
        from rdflib import URIRef

        known = shacl_terms()
        offenders = set()
        for triple in merged_graph():
            for term in triple:
                if not isinstance(term, URIRef):
                    continue
                text = str(term)
                if text.startswith(SH) and text != SH and text not in known:
                    offenders.add(text)
        self.assertEqual(
            [],
            sorted(offenders),
            offenders_message(
                "terms in the SHACL namespace that SHACL does not define, so "
                "every engine ignores them",
                sorted(offenders),
            ),
        )


class ContradictoryConstraintTest(unittest.TestCase):
    """Pairs of constraints that no node can ever satisfy together."""

    def assertNoRows(self, sparql, explanation):
        require_rdflib()
        rows = query(merged_graph(), sparql)
        self.assertEqual(
            [],
            sorted(rows, key=str),
            offenders_message(explanation, sorted(rows, key=str)),
        )

    def test_min_count_never_exceeds_max_count(self):
        self.assertNoRows(
            "select ?shape ?min ?max { ?shape sh:minCount ?min ; sh:maxCount ?max "
            "filter(?min > ?max) }",
            "shapes with sh:minCount greater than sh:maxCount, which no node can satisfy",
        )

    def test_no_shape_has_both_sh_datatype_and_sh_class(self):
        self.assertNoRows(
            "select ?shape ?datatype ?class { ?shape sh:datatype ?datatype ; sh:class ?class }",
            "shapes requiring a value to be both a literal (sh:datatype) and a "
            "resource (sh:class)",
        )

    def test_no_shape_has_both_nodekind_iri_and_sh_datatype(self):
        self.assertNoRows(
            "select ?shape ?datatype { ?shape sh:nodeKind sh:IRI ; sh:datatype ?datatype }",
            "shapes requiring a value to be both an IRI and a literal",
        )

    def test_no_closed_shape_is_without_properties(self):
        """sh:closed true with no sh:property forbids every property."""
        self.assertNoRows(
            "select ?shape { ?shape sh:closed true "
            "filter not exists { ?shape sh:property ?p } }",
            "sh:closed shapes that permit no property at all",
        )


class ShapeCompletenessTest(unittest.TestCase):
    """Shapes that are structurally incomplete."""

    def assertNoRows(self, sparql, explanation):
        require_rdflib()
        rows = query(merged_graph(), sparql)
        self.assertEqual(
            [],
            sorted(rows, key=str),
            offenders_message(explanation, sorted(rows, key=str)),
        )

    def test_every_property_shape_has_a_path(self):
        self.assertNoRows(
            "select ?propertyShape { ?shape sh:property ?propertyShape "
            "filter not exists { ?propertyShape sh:path ?path } }",
            "sh:property objects with no sh:path, so they constrain nothing",
        )

    def test_every_severity_is_a_standard_shacl_severity(self):
        self.assertNoRows(
            "select ?shape ?severity { ?shape sh:severity ?severity "
            "filter(?severity not in (sh:Violation, sh:Warning, sh:Info)) }",
            "sh:severity values outside sh:Violation / sh:Warning / sh:Info",
        )

    def test_every_sparql_constraint_has_a_message(self):
        """Without sh:message a violation report cannot say what went wrong."""
        self.assertNoRows(
            "select ?constraint { ?constraint rdf:type sh:SPARQLConstraint "
            "filter not exists { ?constraint sh:message ?message } }",
            "sh:SPARQLConstraint without sh:message",
        )

    @unittest.expectedFailure
    def test_every_sh_group_refers_to_a_declared_property_group(self):
        """KNOWN DEFECT: 1 sh:group value is never typed sh:PropertyGroup.

        Report tooling groups and orders findings by sh:PropertyGroup, so a
        dangling reference drops those findings out of the grouping.
        """
        self.assertNoRows(
            "select distinct ?group { ?shape sh:group ?group "
            "filter not exists { ?group rdf:type sh:PropertyGroup } }",
            "sh:group values that are not declared as sh:PropertyGroup",
        )


class CrossFileTest(unittest.TestCase):
    def test_no_node_shape_iri_is_declared_in_two_files(self):
        """Two files defining one shape IRI merge into a single shape.

        Whatever each file says is silently unioned, which is how #153 came
        about. Green today; this keeps it that way.
        """
        require_rdflib()
        from rdflib import URIRef
        from rdflib.namespace import RDF

        seen = {}
        for path in shacl_files():
            from helpers import graph_of

            for shape in set(graph_of(path).subjects(RDF.type, URIRef(SH + "NodeShape"))):
                seen.setdefault(str(shape), []).append(rel(path))
        offenders = sorted(
            (iri, files) for iri, files in seen.items() if len(files) > 1
        )
        self.assertEqual(
            [],
            offenders,
            offenders_message(
                "NodeShape IRIs declared in more than one file",
                offenders,
                render=lambda o: "%s\n    %s" % (o[0], "\n    ".join(o[1])),
            ),
        )


if __name__ == "__main__":
    unittest.main()
