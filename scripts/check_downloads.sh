#!/bin/sh
# Run the download check on this Mac, the way the GitHub workflow runs it.
#
# The check phase stops at EndOfCheckPhase, so it fetches the page or the
# release, asks the server whether the file changed, and does nothing else.
# Nothing is mounted, unpacked or verified, and a download that AutoPkg already
# has in its cache is not fetched again.
#
# Usage:
#   scripts/check_downloads.sh                                   the whole list
#   scripts/check_downloads.sh com.github.jrmfong.download.SnowSQL   one or more
#
# Each identifier is turned into the recipe file in this working copy, so an
# uncommitted fix is what gets tested. A parent from another repo still comes
# from your cloned repos. The list lives in scripts/check_downloads.txt.
set -eu
cd "$(dirname "$0")/.."

if [ "$#" -eq 0 ]; then
  set -- $(grep -v "^#" scripts/check_downloads.txt)
fi

paths=''
for identifier in "$@"; do
  path=$(grep -l "^Identifier: $identifier\$" */*.recipe.yaml | head -1)
  if [ -z "$path" ]; then
    echo "No recipe in this repo has the identifier $identifier" >&2
    exit 1
  fi
  paths="$paths
$path"
done

printf '%s\n' "$paths" | sed '/^$/d' > "${TMPDIR:-/tmp}/check_downloads.list"
echo "Checking $(wc -l < "${TMPDIR:-/tmp}/check_downloads.list" | tr -d ' ') recipe(s) from this working copy."
exec autopkg run --check -v --recipe-list "${TMPDIR:-/tmp}/check_downloads.list"
