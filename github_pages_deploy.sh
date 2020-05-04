#!/bin/sh

git fetch
git rebase origin/master

rm -rf ./docs
cp -r $1 docs  # e.g. ~/python-client/docs/_build/html

git add --all
git commit -m "Automatic Commit; deploying at `date`"
git push
