"""Regression test for issue #154 -- duplicated props in `*-AllowedProperties`.

https://github.com/entsoe/application-profiles-library/issues/154

An `*-AllowedProperties` shape is `sh:closed true` plus one blank `sh:property`
per permitted property. Listing a property twice does not change what the shape
accepts, so nothing fails and nothing warns -- it just means the generator that
produced the file emitted the inherited properties more than once. That is worth
catching, because a generator that duplicates properties is equally capable of
dropping one.

This is the worked example for why `graph_of()` exists: the defect is a repeated
statement inside a single file, so it must be counted per file. Counting it in
the merged graph would also flag any shape IRI that two files legitimately
contribute to.

KNOWN DEFECT, tracked by #154: 948 duplicated (shape, property) pairs, all in
three NCP files:

    NCP/SHACL/EquipmentReliability-AP-Con-Simple-SHACL.ttl   577
    NCP/SHACL/SteadyStateInstruction-AP-Con-Simple-SHACL.ttl 187
    NCP/SHACL/GridDisturbance-AP-Con-Simple-SHACL.ttl        184

The issue is closed but the SHACL still carries the duplicates, so the test
stays marked until they are gone.
"""

import unittest

from helpers import graph_of, offenders_message, query, rel, require_rdflib, shacl_files


class AllowedPropertiesTest(unittest.TestCase):
    @unittest.expectedFailure
    def test_no_shape_lists_the_same_property_twice(self):
        require_rdflib()
        offenders = []
        for path in shacl_files():
            rows = query(
                graph_of(path),
                """
                select ?nodeShape ?path (count(*) as ?n) {
                  ?nodeShape sh:property ?propertyShape .
                  ?propertyShape sh:path ?path
                  filter(isblank(?propertyShape))
                }
                group by ?nodeShape ?path having(count(*) > 1)
                """,
            )
            offenders.extend(
                (rel(path), str(r[0]), str(r[1]), int(r[2])) for r in rows
            )
        self.assertEqual(
            [],
            offenders,
            offenders_message(
                "shapes listing the same property more than once, see issue #154",
                offenders,
                render=lambda o: "%s: %s lists %s %d times" % o,
            ),
        )


if __name__ == "__main__":
    unittest.main()
