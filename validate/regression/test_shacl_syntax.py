"""The baseline every other SHACL test depends on: it all parses.

`make rdf-validate` and `make sparql-validate` cover the same ground with Jena,
but they only write a report -- nothing fails when the report is non-empty, and
they need Jena on PATH. These turn the same two checks into assertions that run
anywhere Python and rdflib do.

Context: issues #63 (SHACL files are not validated regularly), #70 (SPARQL
syntax errors) and #74 (validate SHACL before publication).
"""

import unittest

from helpers import (
    SH,
    as_sparql,
    graph_of,
    merged_graph,
    offenders_message,
    prefixes,
    rel,
    require_rdflib,
    shacl_files,
    sparql_prefix_block,
)


class TurtleSyntaxTest(unittest.TestCase):
    def test_every_shacl_file_parses_as_turtle(self):
        require_rdflib()
        files = shacl_files()
        self.assertNotEqual([], files, "no SHACL files found")
        for path in files:
            with self.subTest(file=rel(path)):
                graph_of(path)  # raises on a syntax error

    def test_no_shacl_file_starts_with_a_utf8_bom(self):
        for path in shacl_files():
            with self.subTest(file=rel(path)):
                head = path.read_bytes()[:3]
                self.assertNotEqual(
                    b"\xef\xbb\xbf", head, "%s: starts with a UTF-8 BOM" % rel(path)
                )


class SparqlSyntaxTest(unittest.TestCase):
    """Every sh:select must parse, both the lenient way and the strict way."""

    def selects(self):
        require_rdflib()
        from rdflib import URIRef

        graph = merged_graph()
        found = list(graph.subject_objects(URIRef(SH + "select")))
        self.assertNotEqual([], found, "no sh:select constraints found")
        return graph, found

    def test_every_sh_select_parses_with_the_shared_prefixes(self):
        """Lenient: prepend validate/prefixes.rq, the union of all declarations."""
        _, selects = self.selects()  # skips the test if rdflib is missing
        from rdflib.plugins.sparql import prepareQuery

        prefix_block = prefixes()
        for shape, select in selects:
            with self.subTest(shape=str(shape)):
                try:
                    prepareQuery(prefix_block + "\n" + as_sparql(select))
                except Exception as exc:  # noqa: BLE001 -- report, don't swallow
                    self.fail("%s\n%s" % (shape, exc))

    def test_every_sh_select_parses_with_only_its_own_sh_prefixes(self):
        """Strict, and the one that matches production.

        A validation engine resolves prefixed names through the constraint's own
        sh:prefixes / sh:declare chain and through nothing else. A query that
        needs a prefix its sh:prefixes does not reach parses fine above and still
        fails in the field. Both are green today. Before PR #151 replaced the
        DatasetMetadata cardinality queries, `dm:requires-NC-cardinalitySparql`
        failed both, and the committed sparql-validate.txt had been recording it
        as `Unresolved prefixed name: https:` with nothing failing.
        """
        graph, selects = self.selects()  # skips the test if rdflib is missing
        from rdflib.plugins.sparql import prepareQuery

        unreachable = []
        for shape, select in selects:
            with self.subTest(shape=str(shape)):
                block = sparql_prefix_block(graph, shape)
                if not block:
                    unreachable.append(shape)
                try:
                    prepareQuery(block + "\n" + as_sparql(select))
                except Exception as exc:  # noqa: BLE001 -- report, don't swallow
                    self.fail("%s\n%s" % (shape, exc))
        self.assertEqual(
            [],
            unreachable,
            offenders_message(
                "SPARQL constraints with no sh:prefixes, so no prefixed name in "
                "them can resolve",
                unreachable,
            ),
        )


if __name__ == "__main__":
    unittest.main()
