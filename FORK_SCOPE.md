# Scope of this fork

Upstream: [weaviate/weaviate-python-client](https://github.com/weaviate/weaviate-python-client). Original authorship and license
remain with upstream; upstream performance/clinical claims are not personal
portfolio results.

Contribution fork of the upstream Python SDK. Confirmed personal contributions are [DigitalOcean generative integration #2153](https://github.com/weaviate/weaviate-python-client/pull/2153) and [read-only backup permissions #2186](https://github.com/weaviate/weaviate-python-client/pull/2186). Authorship of those patches does not imply authorship of the whole SDK.

## Audited snapshot and limits

Portfolio audit base: `38f30c11cd7531da5ab61246d56aa61410cca11c` (2026-10-28, rechecked 2026-10-29).

The audited default snapshot predates the #2186 merge and is not a current supported distribution. Development/integration requirement pins had advisory matches. Use a supported upstream release for new applications; this historical fork is not a dependency or operational qualification. External Weaviate/DigitalOcean integration was not run during remediation.

This note changes attribution and usage guidance only. It does not certify the
upstream code, refresh its full dependency tree, or claim newly executed tests.
