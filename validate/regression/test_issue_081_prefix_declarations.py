"""Regression test for issue #81 -- duplicate PrefixDeclarations.

https://github.com/entsoe/application-profiles-library/issues/81
https://github.com/entsoe/application-profiles-library/issues/8

A `sh:select` resolves its prefixed names through `sh:prefixes` / `sh:declare`.
When the same prefix is declared twice, or bound to two different namespaces in
two different files, which one a constraint gets depends on what the engine
happened to load -- so the same shape can validate differently in two
deployments. `validate/README.md` already works around it with `select distinct`
when extracting `prefixes.rq`.

KNOWN DEFECTS, tracked by #81 and #8:

* 2 prefixes are bound to more than one namespace (the `cim:` / `eu:` version
  split described in #8)
* 5 (subject, prefix) pairs are declared more than once

Remove the @unittest.expectedFailure decorators as each is fixed.
"""

import unittest

from helpers import merged_graph, offenders_message, query, require_rdflib


class PrefixDeclarationTest(unittest.TestCase):
    @unittest.expectedFailure
    def test_each_prefix_is_bound_to_exactly_one_namespace(self):
        require_rdflib()
        rows = query(
            merged_graph(),
            """
            select ?prefix (count(distinct ?namespace) as ?n) {
              ?owner sh:declare [ sh:prefix ?prefix ; sh:namespace ?namespace ]
            }
            group by ?prefix having(count(distinct ?namespace) > 1)
            """,
        )
        self.assertEqual(
            [],
            sorted(rows, key=str),
            offenders_message(
                "prefixes bound to more than one namespace, see issues #81 and #8",
                sorted(rows, key=str),
                render=lambda r: "%s: %s namespaces" % (r[0], r[1]),
            ),
        )

    @unittest.expectedFailure
    def test_no_prefix_is_declared_twice_on_the_same_subject(self):
        require_rdflib()
        rows = query(
            merged_graph(),
            """
            select ?owner ?prefix (count(*) as ?n) {
              ?owner sh:declare [ sh:prefix ?prefix ; sh:namespace ?namespace ]
            }
            group by ?owner ?prefix having(count(*) > 1)
            """,
        )
        self.assertEqual(
            [],
            sorted(rows, key=str),
            offenders_message(
                "prefixes declared more than once, see issue #81",
                sorted(rows, key=str),
                render=lambda r: "%s declares %s: %s times" % (r[0], r[1], r[2]),
            ),
        )


if __name__ == "__main__":
    unittest.main()
