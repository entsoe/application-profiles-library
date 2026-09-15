"""Internal consistency: shapes that exist but do no work.

The two checks named in "Check for Internal Consistency",
https://github.com/Sveino/Inst4CIM-KG/tree/develop/shacl-improved, adapted to
how these profiles are actually written.

The published version of the first check is "each NodeShape should have a
property". Applied literally here it flags 25 shapes, and 24 of them are fine:
they constrain through `sh:or`, `sh:and`, `sh:xone` or a SPARQL `sh:target`
instead of through `sh:property`. So the check below asks the question that
actually matters -- does the shape impose *any* constraint -- and that leaves
exactly one real offender.
"""

import unittest

from helpers import SH, merged_graph, offenders_message, require_rdflib

# Every SHACL predicate that makes a shape constrain something. A NodeShape
# carrying none of these accepts every node it targets.
CONSTRAINING_PREDICATES = (
    "property sparql and or xone not node closed class datatype nodeKind "
    "minCount maxCount minLength maxLength pattern languageIn uniqueLang in "
    "hasValue equals disjoint lessThan lessThanOrEquals minInclusive "
    "maxInclusive minExclusive maxExclusive qualifiedValueShape"
).split()


class VacuousShapeTest(unittest.TestCase):
    @unittest.expectedFailure
    def test_every_node_shape_constrains_something(self):
        """KNOWN DEFECT: 1.

        `<http://iec.ch/TC57/ns/CIM/DiagramLayout-EU/Constraints#DiagramObjectGluePoint>`
        is `a sh:NodeShape` with a `sh:targetClass` and nothing else, so it
        selects every DiagramObjectGluePoint in the data and then permits all of
        them. Either it is missing its constraints or it should be removed.
        """
        require_rdflib()
        from rdflib import URIRef
        from rdflib.namespace import RDF

        graph = merged_graph()
        predicates = [URIRef(SH + p) for p in CONSTRAINING_PREDICATES]
        offenders = sorted(
            str(shape)
            for shape in graph.subjects(RDF.type, URIRef(SH + "NodeShape"))
            if not any((shape, p, None) in graph for p in predicates)
        )
        self.assertEqual(
            [],
            offenders,
            offenders_message(
                "NodeShapes that impose no constraint, so every targeted node "
                "conforms",
                offenders,
            ),
        )


class UnusedShapeTest(unittest.TestCase):
    def test_every_named_property_shape_is_referenced(self):
        """Green, and worth keeping green -- it is easy to get wrong.

        Counting only `sh:property` references reports three false positives in
        `DatasetMetadata-AP-Con-SHACL.ttl`: `dm:conformsToNCProfile` and two
        siblings are reached through `sh:not`, which is a perfectly good way to
        use a shape. Any incoming reference counts.
        """
        require_rdflib()
        from rdflib import URIRef
        from rdflib.namespace import RDF

        graph = merged_graph()
        named = [
            s
            for s in graph.subjects(RDF.type, URIRef(SH + "PropertyShape"))
            if isinstance(s, URIRef)
        ]
        self.assertNotEqual([], named, "no named PropertyShapes found")
        offenders = sorted(
            str(s) for s in named if not any(graph.subject_predicates(s))
        )
        self.assertEqual(
            [],
            offenders,
            offenders_message(
                "named PropertyShapes nothing refers to, so no engine will ever "
                "evaluate them",
                offenders,
            ),
        )


if __name__ == "__main__":
    unittest.main()
