#!/usr/bin/env bash
set -xeuo pipefail

TARGET_REF="${TARGET_REF:-master}"

VERSION=$(python - <<'PY'
import pathlib
import re
import tomllib

pyproject = pathlib.Path('../python-client/pyproject.toml')
if pyproject.exists():
    print(tomllib.loads(pyproject.read_text(encoding='utf-8'))['project']['version'])
else:
    conf_text = pathlib.Path('../python-client/docs/conf.py').read_text(encoding='utf-8')
    match = re.search(r"release\s*=\s*['\"]([^'\"]+)['\"]", conf_text)
    if not match:
        raise RuntimeError('Unable to determine version from pyproject.toml or conf.py')
    print(match.group(1))
PY
)
MAJOR_MINOR="v$(echo "$VERSION" | cut -d. -f1,2)"

mkdir -p docs
if [ "$TARGET_REF" = "master" ] || [ "$TARGET_REF" = "main" ]; then
  find docs -mindepth 1 -maxdepth 1 ! -name 'v*' ! -name 'latest' -exec rm -rf {} +
  cp -r ../python-client/docs/_build/html/. ./docs/
  rm -rf "docs/latest"
  mkdir -p "docs/latest"
  cp -r ../python-client/docs/_build/html/. "docs/latest/"
fi

rm -rf "docs/$MAJOR_MINOR"
mkdir -p "docs/$MAJOR_MINOR"
cp -r ../python-client/docs/_build/html/. "docs/$MAJOR_MINOR/"

# Only tracked, modified files can have a timestamp-only diff to restore.
# New files have an empty git diff but must be kept for publication.
while IFS= read -r -d '' rst; do
  if git diff --quiet -I 'sphinx-quickstart on' -- "$rst"; then
    git checkout -- "$rst"
  fi
done < <(git diff --name-only --diff-filter=M -z -- 'docs/**/_sources/index.rst.txt' 'docs/_sources/index.rst.txt')

git --no-pager status --short
