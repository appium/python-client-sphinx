import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'update_docs.sh'
INDEX = '_sources/index.rst.txt'


class UpdateDocsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.repo = root / 'python-client-sphinx'
        self.repo.mkdir()
        self.html = root / 'python-client/docs/_build/html'
        self.html.mkdir(parents=True)
        (root / 'python-client/pyproject.toml').write_text(
            '[project]\nversion = "6.0.1"\n'
        )
        self.git('init', '-q')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.com')

    def git(self, *args):
        return subprocess.run(
            ['git', *args], cwd=self.repo, check=True,
            capture_output=True, text=True,
        ).stdout

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'Initial documentation')

    def update(self, ref='master'):
        env = dict(os.environ, TARGET_REF=ref)
        # The production workflow exposes Python as `python`.
        bin_dir = Path(self.temp.name) / 'bin'
        bin_dir.mkdir(exist_ok=True)
        python = bin_dir / 'python'
        if not python.exists():
            python.symlink_to(sys.executable)
        env['PATH'] = str(bin_dir) + os.pathsep + env['PATH']
        result = subprocess.run(
            ['bash', str(SCRIPT)], cwd=self.repo, env=env,
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_new_index_is_kept(self):
        # Keep _sources tracked so git status lists the new file individually.
        self.write(self.repo / 'docs/_sources/other.rst.txt', 'Other page\n')
        self.commit()
        self.write(self.html / INDEX, 'New index\n')
        self.update()
        for target in ('docs', 'docs/latest', 'docs/v6.0'):
            self.assertEqual((self.repo / target / INDEX).read_text(), 'New index\n')

    def test_timestamp_only_changes_are_reverted_in_all_targets(self):
        old = 'Title\n   sphinx-quickstart on yesterday.\n'
        new = 'Title\n   sphinx-quickstart on today.\n'
        for target in ('docs', 'docs/latest', 'docs/v6.0'):
            self.write(self.repo / target / INDEX, old)
        self.commit()
        self.write(self.html / INDEX, new)
        self.update()
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_content_changes_are_kept(self):
        self.write(self.repo / 'docs' / INDEX, 'Old title\n   sphinx-quickstart on yesterday.\n')
        self.commit()
        new = 'New title\n   sphinx-quickstart on today.\n'
        self.write(self.html / INDEX, new)
        self.update()
        self.assertEqual((self.repo / 'docs' / INDEX).read_text(), new)

    def test_release_build_preserves_root_latest_and_other_versions(self):
        for target in ('docs', 'docs/latest', 'docs/v5.0', 'docs/v6.0'):
            self.write(self.repo / target / 'index.html', target)
        self.write(self.repo / 'docs/v6.0/obsolete.html', 'obsolete')
        self.commit()
        self.write(self.html / 'index.html', 'Release documentation')
        self.update(ref='v6.0.1')
        for target in ('docs', 'docs/latest', 'docs/v5.0'):
            self.assertEqual((self.repo / target / 'index.html').read_text(), target)
        self.assertEqual(
            (self.repo / 'docs/v6.0/index.html').read_text(), 'Release documentation'
        )
        self.assertFalse((self.repo / 'docs/v6.0/obsolete.html').exists())

    def test_master_build_preserves_other_versions_and_removes_stale_files(self):
        self.write(self.repo / 'docs/v5.0/index.html', 'Previous release')
        for target in ('docs', 'docs/latest', 'docs/v6.0'):
            self.write(self.repo / target / 'obsolete.html', 'obsolete')
        self.commit()
        self.write(self.html / 'index.html', 'Current documentation')
        self.update()
        self.assertEqual(
            (self.repo / 'docs/v5.0/index.html').read_text(), 'Previous release'
        )
        for target in ('docs', 'docs/latest', 'docs/v6.0'):
            self.assertEqual(
                (self.repo / target / 'index.html').read_text(), 'Current documentation'
            )
            self.assertFalse((self.repo / target / 'obsolete.html').exists())


if __name__ == '__main__':
    unittest.main()
