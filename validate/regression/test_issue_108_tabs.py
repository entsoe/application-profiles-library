"""Regression test for issue #108 -- "restore tabs in shacl-sparql-stats.tsv".

https://github.com/entsoe/application-profiles-library/issues/108

Issue #69 ("don't use tabs, use only spaces") was applied as a blanket
tabs-to-spaces conversion, which also hit the two places where a TAB carries
meaning:

* ``validate/Makefile`` -- GNU make requires every recipe line to start with a
  literal TAB. With spaces it refuses to run at all::

      Makefile:2: *** missing separator.  Stop.

* ``validate/*.tsv`` -- TSV means tab separated. Without tabs GitHub declines
  to render the file: "No tabs found in this TSV file in line 0."

Neither breakage shows up in ``make rdf-validate`` or ``make sparql-validate``,
so it is pinned down here instead.
"""

import csv
import io
import re
import unittest

from helpers import VALIDATE_DIR, read_text, rel

MAKEFILE = VALIDATE_DIR / "Makefile"
STATS_TSV = VALIDATE_DIR / "shacl-sparql-stats.tsv"

# A target line, eg "rdf-validate:" or "zip: # comment". Excludes variable
# assignments such as "FOO := bar".
TARGET_RE = re.compile(r"^[A-Za-z0-9_.%/-]+\s*:(?!=)")


class MakefileTabsTest(unittest.TestCase):
    """The Makefile must keep the TABs GNU make needs."""

    def setUp(self):
        self.lines = read_text(MAKEFILE).split("\n")

    def test_no_line_is_indented_with_spaces(self):
        offenders = [
            (n, line)
            for n, line in enumerate(self.lines, start=1)
            if line.startswith(" ")
        ]
        self.assertEqual(
            [],
            offenders,
            "%s: lines indented with spaces instead of a TAB -- GNU make will "
            "fail with 'missing separator'. See issue #108.\n%s"
            % (
                rel(MAKEFILE),
                "\n".join("  line %d: %r" % (n, line) for n, line in offenders),
            ),
        )

    def test_every_target_is_followed_by_a_tab_indented_recipe(self):
        offenders = []
        for n, line in enumerate(self.lines, start=1):
            if not TARGET_RE.match(line):
                continue
            following = next(
                (
                    (m, nxt)
                    for m, nxt in enumerate(self.lines[n:], start=n + 1)
                    if nxt.strip()
                ),
                None,
            )
            if following is None or not following[1].startswith("\t"):
                offenders.append((n, line))
        self.assertEqual(
            [],
            offenders,
            "%s: target(s) whose recipe does not start with a TAB. See issue #108.\n%s"
            % (
                rel(MAKEFILE),
                "\n".join("  line %d: %r" % (n, line) for n, line in offenders),
            ),
        )


class TsvTabsTest(unittest.TestCase):
    """Every .tsv under validate/ must really be tab separated."""

    def tsv_files(self):
        files = sorted(VALIDATE_DIR.rglob("*.tsv"))
        self.assertNotEqual([], files, "no .tsv files found under %s" % rel(VALIDATE_DIR))
        return files

    def test_first_line_contains_a_tab(self):
        """The exact condition GitHub reports as 'No tabs found ... in line 0'."""
        for path in self.tsv_files():
            with self.subTest(file=rel(path)):
                first = read_text(path).split("\n", 1)[0]
                self.assertIn(
                    "\t",
                    first,
                    "%s: header has no TAB, so GitHub will not render it as a "
                    "table. See issue #108.\n  %r" % (rel(path), first),
                )

    def test_all_rows_have_the_same_number_of_non_empty_fields(self):
        for path in self.tsv_files():
            with self.subTest(file=rel(path)):
                rows = list(
                    csv.reader(io.StringIO(read_text(path)), delimiter="\t")
                )
                rows = [r for r in rows if r and any(f.strip() for f in r)]
                self.assertGreater(len(rows), 1, "%s: no data rows" % rel(path))
                width = len(rows[0])
                self.assertGreaterEqual(
                    width, 2, "%s: header splits into %d field(s) on TAB" % (rel(path), width)
                )
                offenders = [
                    (n, r) for n, r in enumerate(rows, start=1) if len(r) != width
                ]
                self.assertEqual(
                    [],
                    offenders,
                    "%s: expected %d tab-separated fields per row. See issue #108.\n%s"
                    % (
                        rel(path),
                        width,
                        "\n".join(
                            "  line %d: %d field(s): %r" % (n, len(r), r)
                            for n, r in offenders[:10]
                        ),
                    ),
                )

    def test_stats_tsv_matches_what_shacl_sparql_pl_writes(self):
        """shacl-sparql.pl writes "name\tchars\tlines" plus integer columns."""
        rows = [
            r
            for r in csv.reader(io.StringIO(read_text(STATS_TSV)), delimiter="\t")
            if r and any(f.strip() for f in r)
        ]
        self.assertEqual(
            ["name", "chars", "lines"],
            rows[0],
            "%s: unexpected header. See issue #108." % rel(STATS_TSV),
        )
        for n, (name, chars, lines) in enumerate(rows[1:], start=2):
            with self.subTest(line=n):
                self.assertNotEqual("", name.strip(), "empty shape name")
                self.assertRegex(chars, r"^\d+$", "chars is not an integer")
                self.assertRegex(lines, r"^\d+$", "lines is not an integer")


if __name__ == "__main__":
    unittest.main()
