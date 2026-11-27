# Appium Python Client documentation

GitHub Pages serves the [documentation](https://appium.github.io/python-client-sphinx/)
from `master:docs/`. The scheduled build publishes the Python client's
development branch at the site root and at `latest/`.

To publish a release line, run the Python CI workflow with its git tag.
For example, a build of `v6.3.0` updates `v6.3/`. Development builds
preserve these versioned pages. Each documentation update regenerates
`switcher.json` from the directories that have a published landing page.
