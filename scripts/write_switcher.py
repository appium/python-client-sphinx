"""Build the PyData version menu from documentation present on GitHub Pages."""

import json
import re
from pathlib import Path


def write_switcher(docs: Path) -> None:
    base_url = 'https://appium.github.io/python-client-sphinx/'
    entries = []
    if (docs / 'latest/index.html').is_file():
        entries.append({'name': 'Development', 'version': 'latest', 'url': base_url + 'latest/'})

    releases = []
    for index in docs.glob('v*/index.html'):
        match = re.fullmatch(r'v(\d+)\.(\d+)', index.parent.name)
        if match:
            releases.append((int(match[1]), int(match[2]), index.parent.name))

    for major, minor, directory in sorted(releases, reverse=True):
        entries.append({'name': f'{major}.{minor}.x', 'version': directory, 'url': f'{base_url}{directory}/'})
    (docs / 'switcher.json').write_text(json.dumps(entries, indent=2) + '\n')


if __name__ == '__main__':
    write_switcher(Path('docs'))
