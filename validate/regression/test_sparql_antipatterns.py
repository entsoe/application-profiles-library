"""Anti-patterns inside `sh:select`, from issues #70 and #141.

Most of these are green. #70 was fixed in PR #82 and the typed-boolean half of
#141 is clean, so the point of those tests is to keep the fixes fixed: this
SPARQL is generated, and a generator that emitted `"true"^^xsd:boolean` once can
emit it again. The `BIND(EXISTS{...})` half of #141 is still open.
"""

import re
import unittest

from helpers import SH, merged_graph, offenders_message, require_rdflib

# BIND(EXISTS{...} AS ?name), capturing the variable it binds.
BIND_EXISTS = re.compile(
    r"BIND\s*\(\s*EXISTS\s*\{.*?\}\s*AS\s*[?$](\w+)\s*\)", re.I | re.S
)
PROJECTION = re.compile(r"SELECT\s+(?:DISTINCT\s+|REDUCED\s+)?(.*?)\s+WHERE", re.I | re.S)


def selects():
    require_rdflib()
    from rdflib import URIRef

    return list(merged_graph().subject_objects(URIRef(SH + "select")))


class SparqlStructureTest(unittest.TestCase):
    def test_every_sh_select_binds_this(self):
        """A constraint that never mentions $this does not constrain its focus node."""
        offenders = sorted(
            str(shape)
            for shape, select in selects()
            if "$this" not in str(select) and "?this" not in str(select)
        )
        self.assertEqual(
            [],
            offenders,
            offenders_message("sh:select that never mentions $this", offenders),
        )

    def test_no_having_without_group_by(self):
        """HAVING outside a grouped query, issue #70.

        Jena accepts it even with --strict; rdf4j (GraphDB) rejects it with
        `variable 'this' in projection not present in GROUP BY`. A query that
        only runs on some engines is worse than one that runs nowhere, because
        nobody notices.
        """
        offenders = sorted(
            str(shape)
            for shape, select in selects()
            if re.search(r"\bHAVING\b", str(select), re.I)
            and not re.search(r"\bGROUP\s+BY\b", str(select), re.I)
        )
        self.assertEqual(
            [],
            offenders,
            offenders_message(
                "sh:select with HAVING but no GROUP BY, see issue #70", offenders
            ),
        )


class BooleanHandlingTest(unittest.TestCase):
    """Issue #141 -- fix handling of Booleans in SPARQL queries.

    https://github.com/entsoe/application-profiles-library/issues/141

    `?v = "true"^^xsd:boolean` is just `?v`, and `!?v` for the false case.
    `BIND(EXISTS{...} AS ?x) ... FILTER(?x)` is just `FILTER EXISTS{...}`. Both
    contortions are slower and much harder to read.
    """

    def test_no_comparison_against_a_typed_boolean_literal(self):
        """Green; keeping it that way."""
        rx = re.compile(r'"(?:true|false)"\^\^\s*xsd:boolean', re.I)
        offenders = sorted(
            str(shape) for shape, select in selects() if rx.search(str(select))
        )
        self.assertEqual(
            [],
            offenders,
            offenders_message(
                'comparisons against "true"^^xsd:boolean instead of the plain '
                "variable, see issue #141",
                offenders,
            ),
        )

    @unittest.expectedFailure
    def test_no_bind_exists_used_only_as_a_filter(self):
        """KNOWN DEFECT, tracked by #141: 49 constraints.

        Only the constraints that bind the EXISTS result and then never return
        it are flagged. Binding it is legitimate when the value is projected, so
        that the validation report can show it -- `nc:RemedialActionSchedule
        Dependency-associationsSparql` does exactly that with ?a1 ?a2 ?a3, and is
        correctly not counted here. The other 49 all follow the shape

            SELECT $this ?value WHERE {
              BIND(EXISTS{...} AS ?hasvalue) .
              FILTER (?hasvalue=true && ...)
            }

        which is `FILTER EXISTS{...}` written the long way round.
        """
        offenders = []
        for shape, select in selects():
            text = str(select)
            bound = BIND_EXISTS.findall(text)
            if not bound:
                continue
            projection = PROJECTION.search(text)
            projected = projection.group(1) if projection else ""
            unused = [
                name
                for name in bound
                if not re.search(r"[?$]" + re.escape(name) + r"\b", projected)
            ]
            if unused:
                offenders.append((str(shape), unused))
        self.assertEqual(
            [],
            sorted(offenders),
            offenders_message(
                "BIND(EXISTS{...}) results used only in a FILTER, where "
                "FILTER EXISTS{...} would do, see issue #141",
                sorted(offenders),
                render=lambda o: "%s  (%s)" % (o[0], ", ".join("?" + v for v in o[1])),
            ),
        )


if __name__ == "__main__":
    unittest.main()
