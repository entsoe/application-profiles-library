"""Regression test for issue #83 -- shapes that share a local name.

https://github.com/entsoe/application-profiles-library/issues/83

`validate/shacl-sparql.pl` writes one `shacl-sparql/<localname>.rq` per SPARQL
constraint, so shapes sharing a local name silently overwrite each other and the
extraction quietly produces fewer files than there are constraints. Local names
also carry the human identity of a shape in validation reports and in issue
titles, so a clash makes two different constraints indistinguishable to whoever
has to act on the report.

KNOWN DEFECT, tracked by #83: 2 local names, shared by 5 shapes in total.

    PeerTemporalDependency.constraintKind-exclusiveSparql
        AvailabilitySchedule-Complex/2.4, EquipmentReliability-Complex/2.4,
        StateInstructionSchedule-Complex/2.5
    PowerSchedule-currencySparql
        PowerSchedule-Complex/2.5, RemedialActionSchedule-Complex/2.4

Each is a distinct shape in its own profile namespace, so this is not the
harmless `eqn600:BoundaryPoint` case described in `validate/README.md` -- these
genuinely collide on extraction.

Remove @unittest.expectedFailure once the names are made unique.
"""

import unittest

from helpers import SH, local_name, merged_graph, offenders_message, require_rdflib


class ShapeLocalNameTest(unittest.TestCase):
    @unittest.expectedFailure
    def test_sparql_constraint_local_names_are_unique(self):
        require_rdflib()
        from rdflib import URIRef

        by_name = {}
        for shape in merged_graph().subjects(URIRef(SH + "select"), None):
            by_name.setdefault(local_name(shape), set()).add(str(shape))
        offenders = sorted(
            (name, sorted(shapes))
            for name, shapes in by_name.items()
            if len(shapes) > 1
        )
        self.assertEqual(
            [],
            offenders,
            offenders_message(
                "local names used by more than one SPARQL constraint -- "
                "shacl-sparql.pl writes them to the same .rq file, see issue #83",
                offenders,
                render=lambda o: "%s\n    %s" % (o[0], "\n    ".join(o[1])),
            ),
        )


if __name__ == "__main__":
    unittest.main()
