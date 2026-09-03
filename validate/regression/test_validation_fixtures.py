"""Golden fixtures: do the shapes actually catch what they are written to catch?

Every other test in this suite reads the shapes. This one runs them. A
constraint can parse cleanly, reference only declared terms, pass SHACL-SHACL,
and still validate the wrong thing -- a `>` that should be `>=`, a path pointing
one hop too far, a SPARQL filter that never matches. Nothing but running it
against data will tell you.

Each fixture is a directory under `fixtures/`:

    fixtures/<name>/
        shapes.txt      repo-relative SHACL files to load, one per line
        conforming.ttl  data that must produce no results at all
        violating.ttl   data that must produce exactly the results in expected.txt
        expected.txt    <focusNode> <sourceShape> <severity>, one per line

Both directions matter. `conforming.ttl` catches a constraint that has become
too strict and now rejects valid data; `violating.ttl` catches one that has
gone slack and no longer rejects anything. Keep the data minimal -- a fixture
is documentation of what a constraint means, and it is only readable if it
contains nothing but the case it is about.

To add one: create the directory, write the two data files, run the suite once
and copy the reported actual results into expected.txt after checking that every
line of it is a result you actually want.
"""

import unittest

from helpers import FIXTURES_DIR, REPO_ROOT, SH, read_text, rel, require


def fixture_dirs():
    if not FIXTURES_DIR.is_dir():
        return []
    return sorted(d for d in FIXTURES_DIR.iterdir() if d.is_dir())


def manifest_lines(path):
    return [
        line.strip()
        for line in read_text(path).split("\n")
        if line.strip() and not line.strip().startswith("#")
    ]


def parse_expected(path):
    """expected.txt -> set of (focusNode, sourceShape, severity)."""
    expected = set()
    for line in manifest_lines(path):
        fields = line.split()
        if len(fields) != 3:
            raise ValueError("%s: expected 3 fields, got %r" % (rel(path), line))
        focus, shape, severity = fields
        expected.add((focus.strip("<>"), shape.strip("<>"), severity))
    return expected


class ValidationFixtureTest(unittest.TestCase):
    def setUp(self):
        require("pyshacl")
        self.assertNotEqual([], fixture_dirs(), "no fixtures found in %s" % rel(FIXTURES_DIR))

    def shapes_graph(self, fixture):
        from rdflib import Graph

        graph = Graph()
        for relative in manifest_lines(fixture / "shapes.txt"):
            path = REPO_ROOT / relative
            self.assertTrue(
                path.is_file(),
                "%s: shapes.txt names a file that does not exist: %s"
                % (rel(fixture / "shapes.txt"), relative),
            )
            graph.parse(str(path), format="turtle")
        return graph

    def results(self, fixture, data_file):
        """Run pySHACL and return the reported results as comparable tuples."""
        from pyshacl import validate
        from rdflib import Graph, URIRef
        from rdflib.namespace import RDF

        data = Graph()
        data.parse(str(fixture / data_file), format="turtle")
        _, report, _ = validate(
            data,
            shacl_graph=self.shapes_graph(fixture),
            advanced=True,  # required for sh:sparql constraints
            inference="none",
        )
        return {
            (
                str(report.value(r, URIRef(SH + "focusNode"))),
                str(report.value(r, URIRef(SH + "sourceShape"))),
                str(report.value(r, URIRef(SH + "resultSeverity"))).rsplit("#", 1)[-1],
            )
            for r in report.subjects(RDF.type, URIRef(SH + "ValidationResult"))
        }

    @staticmethod
    def render(results):
        return "\n".join(
            "  <%s> <%s> %s" % r for r in sorted(results)
        ) or "  (none)"

    def test_conforming_data_produces_no_results(self):
        for fixture in fixture_dirs():
            with self.subTest(fixture=fixture.name):
                actual = self.results(fixture, "conforming.ttl")
                self.assertEqual(
                    set(),
                    actual,
                    "%s/conforming.ttl should validate cleanly, but the shapes "
                    "reported:\n%s" % (fixture.name, self.render(actual)),
                )

    def test_violating_data_produces_exactly_the_expected_results(self):
        for fixture in fixture_dirs():
            with self.subTest(fixture=fixture.name):
                expected = parse_expected(fixture / "expected.txt")
                actual = self.results(fixture, "violating.ttl")
                missing = expected - actual
                unexpected = actual - expected
                self.assertEqual(
                    (set(), set()),
                    (missing, unexpected),
                    "%s/violating.ttl did not validate as expected.\n"
                    "no longer reported (the constraint has gone slack):\n%s\n"
                    "newly reported (the constraint has become stricter):\n%s"
                    % (fixture.name, self.render(missing), self.render(unexpected)),
                )


if __name__ == "__main__":
    unittest.main()
