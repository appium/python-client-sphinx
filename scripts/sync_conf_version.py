#!/usr/bin/env python3
import pathlib
import re
import tomllib


def main() -> None:
    pyproject = pathlib.Path('../pyproject.toml')
    if not pyproject.exists():
        return

    version = tomllib.loads(pyproject.read_text(encoding='utf-8'))['project']['version']
    conf = pathlib.Path('conf.py')
    text = conf.read_text(encoding='utf-8')
    text = re.sub(
        r"^project\s*=\s*['\"].*?['\"]",
        f"project = 'Python client {version}'",
        text,
        flags=re.M,
    )
    text = re.sub(
        r"^release\s*=\s*['\"].*?['\"]",
        f"release = '{version}'",
        text,
        flags=re.M,
    )
    conf.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
