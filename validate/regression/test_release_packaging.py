"""Does everything that should ship actually ship?

Two globs decide what a consumer receives:

* `make zip` in validate/Makefile builds `entsoe-SHACL.zip` from `../*/SHACL/*`
* `.github/workflows/release_packages.yml` zips whole `CGMES/` and `NCP/` trees

A SHACL file that lands outside those patterns -- a new profile directory, a
renamed folder, a file saved as `.shacl` -- is not a validation error anywhere.
It simply is not in the release, and the first sign of it is a user reporting
that a constraint they expect is missing.
"""

import unittest

from helpers import PROFILE_DIRS, REPO_ROOT, VALIDATE_DIR, read_text, rel, shacl_files


class PackagingTest(unittest.TestCase):
    def test_make_zip_glob_covers_every_shacl_file(self):
        """`../*/SHACL/*` evaluated from validate/, against what is on disk."""
        packaged = {
            p.resolve()
            for p in VALIDATE_DIR.glob("../*/SHACL/*")
            if p.is_file()
        }
        expected = {p.resolve() for p in shacl_files()}
        missing = sorted(rel(p) for p in expected - packaged)
        self.assertEqual(
            [],
            missing,
            "SHACL files that `make zip` would leave out of entsoe-SHACL.zip:\n  "
            + "\n  ".join(missing),
        )

    def test_the_makefile_still_uses_that_glob(self):
        """If the recipe changes, the test above is checking the wrong pattern."""
        makefile = read_text(VALIDATE_DIR / "Makefile")
        self.assertIn(
            "../*/SHACL/*",
            makefile,
            "validate/Makefile no longer zips ../*/SHACL/* -- update "
            "test_make_zip_glob_covers_every_shacl_file to match the new pattern.",
        )

    def test_the_release_workflow_packages_every_profile_directory(self):
        workflow = REPO_ROOT / ".github" / "workflows" / "release_packages.yml"
        if not workflow.is_file():
            self.skipTest("%s not present" % rel(workflow))
        text = read_text(workflow)
        missing = [
            d.name for d in PROFILE_DIRS if d.is_dir() and "%s/" % d.name not in text
        ]
        self.assertEqual(
            [],
            missing,
            "profile directories the release workflow does not package: %s"
            % ", ".join(missing),
        )

    def test_no_shacl_file_hides_outside_the_shacl_directories(self):
        """A .ttl holding shapes but living somewhere the packaging never looks."""
        known = {p.resolve() for p in shacl_files()}
        strays = sorted(
            rel(p)
            for d in PROFILE_DIRS
            for p in d.rglob("*.ttl")
            if p.resolve() not in known
        )
        self.assertEqual(
            [],
            strays,
            "Turtle files under CGMES/ or NCP/ that are not in a SHACL/ "
            "directory, so no packaging glob picks them up:\n  " + "\n  ".join(strays),
        )


if __name__ == "__main__":
    unittest.main()
