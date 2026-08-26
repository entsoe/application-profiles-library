"""Regression test for issue #153 -- invalid propShapes with two sh:path.

https://github.com/entsoe/application-profiles-library/issues/153

SHACL is explicit: "A shape has at most one value for sh:path"
(https://www.w3.org/TR/shacl/#property-shapes). The eight offending shapes are
an attempt to cover both `cim:` namespace variants at once (issue #145): one
file gives `http://iec.ch/TC57/CIM100#IdentifiedObject.name`, another gives
`https://cim.ucaiug.io/ns#IdentifiedObject.name`. Each file is valid on its own;
the defect only exists in the union, which is how the shapes ship in
`entsoe-SHACL.zip` and how an engine loads them.

That makes this the worked example for why `merged_graph()` exists: a per-file
check finds nothing here.

Because these shapes are used about 800 times, what an engine does with the
second `sh:path` decides the outcome of a large part of the validation.

KNOWN DEFECT, tracked by #153: 8 property shapes, all `ido:IdentifiedObject.*`.
Remove @unittest.expectedFailure once they are split or namespace-normalised.
"""

import unittest

from helpers import graph_of, merged_graph, offenders_message, query, rel, require_rdflib, shacl_files


class SinglePathTest(unittest.TestCase):
    QUERY = """
        select ?propertyShape (count(distinct ?path) as ?n) {
          ?propertyShape sh:path ?path
        }
        group by ?propertyShape having(count(distinct ?path) > 1)
        """

    @unittest.expectedFailure
    def test_no_property_shape_has_two_sh_path_values_in_the_merged_graph(self):
        require_rdflib()
        rows = query(merged_graph(), self.QUERY)
        self.assertEqual(
            [],
            sorted(rows, key=str),
            offenders_message(
                "property shapes with more than one sh:path once all profiles are "
                "loaded together, which is invalid SHACL, see issue #153",
                sorted(rows, key=str),
                render=lambda r: "%s: %s distinct sh:path values" % (r[0], r[1]),
            ),
        )

    def test_no_property_shape_has_two_sh_path_values_within_one_file(self):
        """Currently green, and the reason the merged check above is needed."""
        require_rdflib()
        offenders = []
        for path in shacl_files():
            for row in query(graph_of(path), self.QUERY):
                offenders.append((rel(path), str(row[0]), int(row[1])))
        self.assertEqual(
            [],
            offenders,
            offenders_message(
                "property shapes with more than one sh:path inside a single file, "
                "see issue #153",
                offenders,
                render=lambda o: "%s: %s has %d sh:path values" % o,
            ),
        )


if __name__ == "__main__":
    unittest.main()
