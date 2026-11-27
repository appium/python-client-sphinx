"""Return the documentation directory for the selected Python client ref."""

import os
import re
import tomllib
from pathlib import Path


def docs_version(client: Path, ref: str) -> str:
    if ref in ('master', 'main'):
        return 'latest'
    metadata = client / 'pyproject.toml'
    if metadata.exists():
        version = tomllib.loads(metadata.read_text())['project']['version']
    else:
        # Older tags specify their version in the Sphinx configuration.
        config = (client / 'docs/conf.py').read_text()
        match = re.search(r"""^release\s*=\s*['"]([^'"]+)['"]""", config, re.M)
        if not match:
            raise ValueError('Missing documentation release')
        version = match.group(1)
    match = re.match(r'^(\d+)\.(\d+)', version)
    if not match:
        raise ValueError(f'Invalid release version: {version}')
    return f'v{match[1]}.{match[2]}'


if __name__ == '__main__':
    print(docs_version(Path('../python-client'), os.environ.get('TARGET_REF', 'master')))
