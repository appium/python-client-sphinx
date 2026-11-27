#!/usr/bin/env bash
set -xeuo pipefail

SCRIPTS_DIR="$(dirname "$0")"
DOCS_VERSION=$(python "$SCRIPTS_DIR/docs_version.py")

mkdir -p docs
if [ "$DOCS_VERSION" = "latest" ]; then
  find docs -mindepth 1 -maxdepth 1 ! -name 'v*' ! -name 'latest' -exec rm -rf {} +
  cp -r ../python-client/docs/_build/html/. ./docs/
fi

rm -rf "docs/$DOCS_VERSION"
mkdir -p "docs/$DOCS_VERSION"
cp -r ../python-client/docs/_build/html/. "docs/$DOCS_VERSION/"
python "$SCRIPTS_DIR/write_switcher.py"

# Only tracked, modified files can have a timestamp-only diff to restore.
# New files have an empty git diff but must be kept for publication.
while IFS= read -r -d '' rst; do
  if git diff --quiet -I 'sphinx-quickstart on' -- "$rst"; then
    git checkout -- "$rst"
  fi
done < <(git diff --name-only --diff-filter=M -z -- 'docs/**/_sources/index.rst.txt' 'docs/_sources/index.rst.txt')

git --no-pager status --short
