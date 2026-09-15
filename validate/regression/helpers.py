"""Shared helpers for the CGMES/NCP SHACL regression suite.

See README.md in this directory for what the suite is for and how to add a test.
"""

import functools
import unittest
from pathlib import Path

REGRESSION_DIR = Path(__file__).resolve().parent
VALIDATE_DIR = REGRESSION_DIR.parent
REPO_ROOT = VALIDATE_DIR.parent
FIXTURES_DIR = REGRESSION_DIR / "fixtures"

PROFILE_DIRS = (REPO_ROOT / "CGMES", REPO_ROOT / "NCP")
SHACL_DIRS = tuple(d / "SHACL" for d in PROFILE_DIRS)
RDFS_DIRS = tuple(d / "RDFS" for d in PROFILE_DIRS)
PREFIXES_RQ = VALIDATE_DIR / "prefixes.rq"

SH = "http://www.w3.org/ns/shacl#"

# rdflib exposes the SHACL vocabulary as a DefinedNamespace, but it cannot carry
# terms that are Python keywords, so those are listed here. Using rdflib rather
# than fetching http://www.w3.org/ns/shacl# keeps the suite offline.
_SH_KEYWORD_TERMS = frozenset(["and", "or", "not", "in", "class", "if", "else"])


def rel(path):
    """Repo-relative posix path, for readable assertion messages."""
    return Path(path).resolve().relative_to(REPO_ROOT).as_posix()


def local_name(iri):
    """The part of an IRI after the last '#' or '/'."""
    text = str(iri)
    for sep in ("#", "/"):
        if sep in text:
            text = text.rsplit(sep, 1)[1] or text
    return text


def read_text(path):
    """Read a text file with line endings normalised to LF.

    Windows checkouts use core.autocrlf=true, so the working tree holds CRLF
    while the committed blob holds LF. No test may depend on which of the two
    it happens to be looking at.
    """
    return Path(path).read_text(encoding="utf-8").replace("\r\n", "\n")


def shacl_files():
    """All published SHACL files, sorted, as a list of Path."""
    return sorted(p for d in SHACL_DIRS for p in d.glob("*.ttl"))


def rdfs_files():
    """All published RDFS vocabularies, sorted, as a list of Path."""
    return sorted(p for d in RDFS_DIRS for p in d.glob("*.rdf"))


def require(module, package=None):
    """Skip the calling test when `module` is not installed."""
    import importlib

    try:
        return importlib.import_module(module)
    except ImportError:
        raise unittest.SkipTest(
            "%s is not installed: pip install -r validate/regression/requirements.txt"
            % (package or module)
        )


def require_rdflib():
    """Skip the calling test when rdflib is not installed."""
    return require("rdflib")


@functools.lru_cache(maxsize=None)
def graph_of(path):
    """Parse one SHACL file into its own rdflib Graph (cached)."""
    require_rdflib()
    from rdflib import Graph

    g = Graph()
    g.parse(str(path), format="turtle")
    return g


@functools.lru_cache(maxsize=None)
def merged_graph():
    """All SHACL files parsed into a single rdflib Graph (cached).

    Per-file and merged evaluation find different defects, so pick deliberately:

    * per-file  -- a shape that repeats a property inside one file, eg issue #154
    * merged    -- a shape IRI that gets conflicting statements from two files,
                   eg issue #153 (two sh:path values, one per namespace variant)

    rdflib mints fresh blank node ids per parse, so merging never conflates
    blank property shapes coming from different files.
    """
    require_rdflib()
    from rdflib import Graph

    g = Graph()
    for f in shacl_files():
        g += graph_of(f)
    return g


@functools.lru_cache(maxsize=None)
def vocabulary_graph():
    """All RDFS profile vocabularies parsed into a single Graph (cached).

    This is what the shapes are supposed to be about: the classes and properties
    a shape may legitimately mention.
    """
    require_rdflib()
    from rdflib import Graph

    g = Graph()
    for f in rdfs_files():
        g.parse(str(f))
    return g


@functools.lru_cache(maxsize=None)
def vocabulary_terms():
    """Every IRI the shipped RDFS vocabularies say something about."""
    from rdflib import URIRef

    return frozenset(
        str(s) for s in vocabulary_graph().subjects() if isinstance(s, URIRef)
    )


@functools.lru_cache(maxsize=None)
def shacl_terms():
    """Every IRI in the SHACL namespace that the SHACL spec defines."""
    require_rdflib()
    from rdflib.namespace import SH as SH_NS

    return frozenset(
        SH + t for t in set(SH_NS.__annotations__) | _SH_KEYWORD_TERMS
    )


def query(graph, sparql):
    """Run SPARQL with sh:/rdf:/rdfs:/xsd: predeclared, return a list of rows."""
    return list(
        graph.query(
            "PREFIX sh: <http://www.w3.org/ns/shacl#>\n"
            "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"
            "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n"
            "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n" + sparql
        )
    )


def prefixes():
    """The SPARQL prefix block shared by all sh:select constraints."""
    return read_text(PREFIXES_RQ)


def sparql_prefix_block(graph, constraint):
    """The PREFIX lines a SPARQL constraint can actually see.

    A validation engine resolves prefixed names in sh:select through the
    sh:prefixes / sh:declare chain of that constraint, and through nothing else.
    """
    from rdflib import URIRef

    declare = URIRef(SH + "declare")
    lines = set()
    for owner in graph.objects(constraint, URIRef(SH + "prefixes")):
        for decl in graph.objects(owner, declare):
            prefix = graph.value(decl, URIRef(SH + "prefix"))
            namespace = graph.value(decl, URIRef(SH + "namespace"))
            if prefix is not None and namespace is not None:
                lines.add("PREFIX %s: <%s>" % (prefix, namespace))
    return "\n".join(sorted(lines))


def as_sparql(select):
    """SHACL's $this / $PATH placeholders are not SPARQL; make them variables."""
    return str(select).replace("$this", "?this").replace("$PATH", "?PATH")


def offenders_message(header, offenders, render=str, limit=20):
    """A failure message that names the offenders instead of just counting them."""
    shown = [render(o) for o in offenders[:limit]]
    if len(offenders) > limit:
        shown.append("... and %d more" % (len(offenders) - limit))
    return "%s (%d)\n%s" % (header, len(offenders), "\n".join("  " + s for s in shown))
