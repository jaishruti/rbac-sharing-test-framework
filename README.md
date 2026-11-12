![CI](https://github.com/jaishruti/rbac-sharing-test-framework/actions/workflows/ci.yml/badge.svg)
# RBAC & Sharing Regression Framework

A data-driven test framework that turns a permission matrix (YAML) into
hundreds of automated checks, with a one-command report and CI wiring.

## Quick start
```
make setup
make test        # green run + HTML report in reports/report.html
make demo-bug    # injects a privilege-escalation bug -> suite goes red
DEMO_BUG=2 make test   # dependency access not revoked on unshare
DEMO_BUG=3 make test   # editor grants a higher role than their own
```

## How it works
| Piece | Role |
|---|---|
| `matrix/permissions.yaml` | Single source of truth: roles x resource types x actions, plus per-type overrides |
| `tests/test_rbac_matrix.py` | Generates one test per matrix cell (108 today). Add a role/type in YAML -> tests appear, no code |
| `tests/test_sharing_rules.py` | Business rules: share/unshare constraints, owner protection, dependency-graph sharing |
| `tests/conftest.py` | `make_resource` fixture + loader. **Swap `Service` for your API client here** |
| `tools/report.py` | JUnit -> HTML report with pass/fail and manual-vs-automated time |
| `.github/workflows/ci.yml` | Runs on every push/PR, uploads the report |
| `sut/service.py` | Demo system under test with bug injection (replace with the real product) |

## Pointing it at a real product
1. Replace `Service` in `conftest.py` with a client exposing `create`, `share`, `unshare`, `can` (API calls or UI driver).
2. Keep `permissions.yaml` as the independent spec (review it with product/eng).
3. Add business rules as small tests in `test_sharing_rules.py`.
4. Set `MANUAL_MINUTES_PER_CASE` in `tools/report.py` to your measured average.

## Interview talking points
- **Problem:** RBAC x many object types x share/unshare explodes combinatorially; manual regression took hours per release and missed cells.
- **Approach:** Separated the *spec* (YAML matrix) from the *checks* (parametrized tests), so coverage scales by editing data, not code.
- **Proof it works:** Demo the clean run, then flip `DEMO_BUG=1` and show the exact failing cell (`knowledge_base-viewer-edit`) pinpointed in seconds.
- **Impact:** 108 checks in ~0.1s vs ~3.6h manual (at 2 min/cell, an assumption to replace with your real figure); runs on every PR.
- **Design choices:** Spec independent of implementation (avoids tautological tests); business rules layered on top of the matrix; JUnit output keeps it tool-agnostic.
- **Next steps:** API-level adapter, UI smoke layer (Playwright), negative/boundary users (cross-org, deactivated), nightly runs with trend dashboard.

Be upfront in interviews that the demo SUT is a simulation, and quote real numbers from your own work for the impact claim.
