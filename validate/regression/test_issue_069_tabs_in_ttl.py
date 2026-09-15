"""Regression test for issue #69 -- "don't use tabs, use only spaces".

https://github.com/entsoe/application-profiles-library/issues/69
https://github.com/entsoe/application-profiles-library/issues/140

Tabs render at a different width in every editor, so indentation that lines up
for the author lines up for nobody else. The SPARQL text inside `sh:select` is
where it hurts most: that text is copied verbatim into
`validate/shacl-sparql/*.rq` and into every error report.

This is the mirror image of test_issue_108_tabs.py. There, a TAB is significant
and must be preserved; here it must not appear at all. Both directions need a
test, because the fix for one is what broke the other.

The sh:select half went green with the #140 indentation fixes merged in #157,
so that one is a plain guard now.

KNOWN DEFECT, tracked by #69: 11 lines across 6 SHACL files still contain a TAB,
all of them Turtle indentation rather than SPARQL text. Remove
@unittest.expectedFailure once they are cleaned up -- the suite will tell you,
because an unexpected success fails the run.
"""

import unittest

from helpers import (
    SH,
    merged_graph,
    offenders_message,
    read_text,
    rel,
    require_rdflib,
    shacl_files,
)


class TabsInTurtleTest(unittest.TestCase):
    @unittest.expectedFailure
    def test_no_shacl_file_contains_a_tab(self):
        offenders = []
        for path in shacl_files():
            for number, line in enumerate(read_text(path).split("\n"), start=1):
                if "\t" in line:
                    offenders.append((rel(path), number, line))
        self.assertEqual(
            [],
            offenders,
            offenders_message(
                "lines containing a TAB, see issue #69",
                offenders,
                render=lambda o: "%s:%d: %r" % o,
            ),
        )

    def test_no_sparql_constraint_contains_a_tab(self):
        """The subset that leaks into shacl-sparql/*.rq and into error reports.

        Green since #157; this keeps it that way.
        """
        require_rdflib()
        from rdflib import URIRef

        offenders = [
            str(shape)
            for shape, select in merged_graph().subject_objects(URIRef(SH + "select"))
            if "\t" in str(select)
        ]
        self.assertEqual(
            [],
            sorted(offenders),
            offenders_message(
                "sh:select text containing a TAB, see issues #69 and #140",
                sorted(offenders),
            ),
        )


if __name__ == "__main__":
    unittest.main()
