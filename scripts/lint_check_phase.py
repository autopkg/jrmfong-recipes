#!/usr/bin/env python3
"""
Check that no recipe opens its download during the check phase.

autopkg --check keeps every step up to the LAST EndOfCheckPhase in the MERGED
parent chain and deletes the rest. A processor placed before that marker runs
during the check phase. A CI runner that restores a cached download leaves an
empty placeholder file in place of the skipped download, so such a processor
reads a file with no contents. Mounting an empty placeholder gives
"hdiutil: attach failed - image not recognized". The recipe then fails because
the skip worked, which reads as a broken recipe rather than a caching problem.

Run it on named recipes, or on all of them with no arguments. Parents outside
this repo are read from the cloned AutoPkg repos, so a chain that reaches one of
those needs the repo cloned. An unresolved chain is reported as unknown, never
as safe.

Exit status is 1 when a recipe is unsafe. An unknown chain fails only under
--strict.
"""

import os
import plistlib
import subprocess
import sys
from pathlib import Path

import yaml

MARKER = "EndOfCheckPhase"

# Processors that read, mount, move or delete the downloaded file. A denylist
# suits this job: a chain runs through third-party recipes using processors
# nobody here has audited, and an allowlist would report most of them.
OPENS_DOWNLOAD = {
    "AppDmgVersioner", "AppPkgCreator", "CodeSignatureVerifier", "Copier",
    "DmgCreator", "FileFinder", "FileMover", "FlatPkgUnpacker", "PathDeleter",
    "PkgCopier", "PkgInfoReader", "PkgPayloadUnpacker", "PlistReader",
    "Unarchiver", "Versioner", "XarExtractSingleFile", "XPathParser",
}

REPO_ROOT = Path(__file__).resolve().parent.parent


def autopkg_repo_dir():
    """
    Read RECIPE_REPO_DIR from the AutoPkg preferences.
    """
    try:
        out = subprocess.run(
            ["defaults", "read", "com.github.autopkg", "RECIPE_REPO_DIR"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None


def repos_dir():
    """
    Find the directory holding the cloned third-party recipe repos.
    """
    candidates = (
        os.getenv("AUTOPKG_REPOS_DIR"),
        autopkg_repo_dir(),
        "/Users/Shared/LocalAutoPkgRunner/AutoPkg/Repos",
        Path.home() / "Library/AutoPkg/RecipeRepos",
    )
    for candidate in candidates:
        if candidate and Path(candidate).is_dir() and any(Path(candidate).iterdir()):
            return Path(candidate)
    return None


def load_recipe(path):
    """
    Read a recipe in either of AutoPkg's 2 formats.
    """
    if path.suffix == ".yaml":
        return yaml.safe_load(path.read_text())
    with path.open("rb") as handle:
        return plistlib.load(handle)


def try_load(path):
    """
    Read a recipe, or return None when it will not parse.

    The cloned repos hold thousands of third-party recipes, and a handful never
    parse. One of those must not stop the lint, and it is not ours to fix.
    """
    try:
        return load_recipe(path)
    except Exception:  # noqa: BLE001 - any parse failure just means "skip it"
        return None


def index_recipes(found):
    """
    Map every identifier to the file that declares it.

    This repo goes in first, so a local parent always wins over a copy of the
    same identifier in a clone.
    """
    index = {}
    sources = [REPO_ROOT.glob("*/*.recipe.yaml")]
    if found:
        sources += [found.glob("*/**/*.recipe"), found.glob("*/**/*.recipe.yaml")]
    for source in sources:
        for path in source:
            recipe = try_load(path)
            if isinstance(recipe, dict) and recipe.get("Identifier"):
                index.setdefault(recipe["Identifier"], path)
    return index


def merged_processors(recipe, index):
    """
    Build the parent-first processor list autopkg would run.

    Returns None when a parent is missing from the index.
    """
    chain = [recipe]
    seen = set()
    while chain[0].get("ParentRecipe"):
        parent_id = chain[0]["ParentRecipe"]
        if parent_id in seen or parent_id not in index:
            return None
        seen.add(parent_id)
        chain.insert(0, load_recipe(index[parent_id]))

    names = []
    for link in chain:
        names += [step["Processor"].split("/")[-1]
                  for step in link.get("Process") or []
                  if isinstance(step, dict) and step.get("Processor")]
    return names


def check_phase(names):
    """
    Apply autopkg's trim rule: keep up to the last marker, drop the rest.
    """
    kept = list(names)
    while kept and kept[-1] != MARKER:
        kept.pop()
    return kept


def report(rows, strict):
    """
    Print the findings and return the exit status.
    """
    unsafe = [r for r in rows if r[1] == "unsafe"]
    unknown = [r for r in rows if r[1] == "unknown"]
    nomarker = [r for r in rows if r[1] == "nomarker"]

    for name, _, detail in unknown:
        print(f"  UNKNOWN  {name}: {detail}")
    for name, _, detail in nomarker:
        print(f"  NO MARKER {name}: {detail}")
    for name, _, detail in unsafe:
        print(f"  UNSAFE   {name}: check phase runs {detail}")

    if nomarker:
        print("\nWith no marker anywhere in the chain, autopkg --check deletes "
              "every step and\nruns nothing. A 2-phase CI runner then never sees "
              "a download, so it never\nstarts the full run. Add EndOfCheckPhase "
              "straight after the download processor.")
        return 1

    if unsafe:
        print("\nEach step listed reads the download, so it meets an empty "
              "placeholder when a\nCI run reuses a cached download. Move "
              "EndOfCheckPhase above those steps. When\nthe steps belong to a "
              "third-party parent, fork that parent into this repo with\nthe "
              "marker moved, then repoint ParentRecipe.")
        return 1

    if unknown:
        # A workstation rarely has every parent repo cloned, so an unresolved
        # chain is normal there. Under --strict it is a real failure.
        print(f"\n{len(unknown)} chain(s) could not be resolved. Clone the "
              "parent repo with\nautopkg repo-add, or set AUTOPKG_REPOS_DIR.")
        if strict:
            return 1
        print("Not failing: an unresolved chain is not proof of a problem.")

    print(f"Check phase is safe in {len(rows) - len(unknown)} of "
          f"{len(rows)} recipe(s).")
    return 0


def main():
    """
    Resolve each recipe's chain and report any that opens its download.
    """
    argv = sys.argv[1:]
    strict = "--strict" in argv
    args = [Path(a) for a in argv if a.endswith(".recipe.yaml")]
    paths = args or sorted(REPO_ROOT.glob("*/*.recipe.yaml"))
    if not paths:
        print("No recipes to check.")
        return 0

    index = index_recipes(repos_dir())
    rows = []
    for path in paths:
        recipe = load_recipe(path)
        names = merged_processors(recipe, index)
        if names is None:
            rows.append((path.name, "unknown",
                         f"cannot resolve parent {recipe.get('ParentRecipe')}"))
            continue
        if MARKER not in names:
            rows.append((path.name, "nomarker",
                         "the merged chain has no EndOfCheckPhase"))
            continue
        opens = [n for n in check_phase(names) if n in OPENS_DOWNLOAD]
        rows.append((path.name, "unsafe" if opens else "safe", ", ".join(opens)))

    return report(rows, strict)


if __name__ == "__main__":
    sys.exit(main())
