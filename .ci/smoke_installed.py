"""Verify the installed wheel from a fresh directory, outside the source checkout."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

env = dict(os.environ)
env.pop("PYTHONPATH", None)
code = """
from pathlib import Path
from importlib.metadata import version
import weaviate
from weaviate.collections.classes.generative import GenerativeConfig
from weaviate.classes.rbac import Actions, Permissions
assert 'site-packages' in str(Path(weaviate.__file__).resolve())
permissions = Permissions.backup(collection='Books', read=True)
assert permissions[0].actions == {Actions.Backups.READ}
assert GenerativeConfig.digitalocean(model='synthetic-model') is not None
print('Installed wheel import/configuration contracts passed:', version('weaviate-client'))
"""
with tempfile.TemporaryDirectory() as tmp:
    subprocess.run([sys.executable, "-c", code], cwd=tmp, env=env, check=True)
