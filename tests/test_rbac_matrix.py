"""Data-driven RBAC matrix: every (resource type x role x action) cell is
one test generated from matrix/permissions.yaml. Adding a role or object
type to the YAML adds tests with zero code changes."""
import pytest

from conftest import MATRIX


@pytest.mark.rbac
@pytest.mark.parametrize(
    "rtype,role,action,allowed",
    [(t, r, a, v) for (t, r, a), v in MATRIX.items()],
    ids=[f"{t}-{r}-{a}" for (t, r, a) in MATRIX],
)
def test_permission_matrix(make_resource, svc, rtype, role, action, allowed):
    rid = make_resource(rtype, role)
    assert svc.can("u1", rid, action) is allowed, (
        f"{role} on {rtype}: '{action}' should be "
        f"{'allowed' if allowed else 'denied'}"
    )
