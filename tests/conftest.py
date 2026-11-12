import pathlib
import sys

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sut.service import Service  # noqa: E402  (swap for your real API client)


def load_matrix():
    spec = yaml.safe_load((ROOT / "matrix" / "permissions.yaml").read_text())
    expected = {}
    for rtype in spec["resource_types"]:
        for role, allowed in spec["default"].items():
            allowed = spec.get("overrides", {}).get(rtype, {}).get(role, allowed)
            for action in spec["actions"]:
                expected[(rtype, role, action)] = action in allowed
    return expected


MATRIX = load_matrix()


@pytest.fixture
def svc():
    return Service()


@pytest.fixture
def make_resource(svc):
    """Create a resource of `rtype` owned by 'owner_u' and put `user` in `role`."""
    def _make(rtype, role, user="u1", deps=()):
        rid = svc.create(rtype, "owner_u", deps=deps)
        if role not in ("none", "owner"):
            svc.acl[(rid, user)] = role
        elif role == "owner":
            svc.acl[(rid, user)] = "owner"
        return rid
    return _make
