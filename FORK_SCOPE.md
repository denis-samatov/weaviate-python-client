# Scope of this fork

Upstream: [weaviate/weaviate-python-client](https://github.com/weaviate/weaviate-python-client). Original authorship and license
remain with upstream; upstream performance/clinical claims are not personal
portfolio results.

Contribution fork of the upstream Python SDK. Confirmed personal contributions are [DigitalOcean generative integration #2153](https://github.com/weaviate/weaviate-python-client/pull/2153) and [read-only backup permissions #2186](https://github.com/weaviate/weaviate-python-client/pull/2186). Authorship of those patches does not imply authorship of the whole SDK.

## Audited snapshot and limits

Portfolio audit base: `38f30c11cd7531da5ab61246d56aa61410cca11c` (2026-10-28, rechecked 2026-10-29).

The audited default snapshot predates the #2186 merge and is not a current supported distribution. Development/integration requirement pins had advisory matches. Use a supported upstream release for new applications; this historical fork is not a dependency or operational qualification. External Weaviate/DigitalOcean integration was not run during remediation.

The historical audit above did not run the new checks described below. These bounded checks do not certify the full upstream system.

## Contribution contracts (2026-10-30)

This branch backports the author's upstream [read-only backup permission contribution #2186](https://github.com/weaviate/weaviate-python-client/pull/2186), because this fork's default base predates that merge. The upstream authorship is retained. `Permissions.backup(read=True)` emits `read_backups`; the existing default and `manage=True` behavior is preserved. Server enforcement needs Weaviate 1.40 or newer and has not been exercised here.

```sh
python -m pip install --require-hashes -r requirements-ci.lock
python -m pip check
python -m pip_audit --no-deps --disable-pip --strict -r requirements-ci.lock
python -m pytest -o addopts= test/test_rbac.py test/test_backup.py test/collection/test_classes_generative.py test/collection/test_generative_metadata.py -q
python -m build --wheel --no-isolation
python -m pip install --no-deps --force-reinstall dist/*.whl
python .ci/smoke_installed.py
python -m pip check
```

The focused suite has 37 offline contracts, including backup serialization/least privilege and generative provider configuration. `-o addopts=` avoids upstream benchmark/xdist CLI defaults whose plugins are outside this profile; assertions are unchanged. The installed-wheel smoke runs outside the checkout and constructs DigitalOcean configuration without calling a provider. CI also checks critical Python lint. These checks do not qualify the whole SDK, legacy development/integration requirements or real Weaviate/DigitalOcean connectivity. Deprecation and package-discovery warnings remain visible. Local shallow builds use an SCM-derived development version, not a published release.

Regenerate tooling/runtime hashes with `uv pip compile requirements-ci.in --python-version 3.13 --generate-hashes -o requirements-ci.lock`. For new applications prefer a maintained upstream release; this contribution fork does not promise full SDK support.
