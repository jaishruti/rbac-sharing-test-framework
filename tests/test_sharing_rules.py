"""Share / unshare business rules and dependency-graph sharing."""
import pytest

from sut.service import PermissionDenied


@pytest.mark.sharing
class TestShareRules:
    def test_viewer_cannot_share(self, svc, make_resource):
        rid = make_resource("folder", "viewer")
        with pytest.raises(PermissionDenied):
            svc.share("u1", rid, "u2", "viewer")

    def test_owner_can_share_and_target_gets_access(self, svc, make_resource):
        rid = make_resource("workflow", "owner")
        svc.share("u1", rid, "u2", "editor")
        assert svc.can("u2", rid, "edit")

    def test_ownership_cannot_be_shared(self, svc, make_resource):
        rid = make_resource("agent", "owner")
        with pytest.raises(PermissionDenied):
            svc.share("u1", rid, "u2", "owner")

    def test_cannot_grant_higher_role_than_own(self, svc, make_resource):
        rid = make_resource("agent", "editor")  # agent editors may share
        with pytest.raises(PermissionDenied):
            svc.share("u1", rid, "u2", "admin")


@pytest.mark.sharing
class TestUnshareRules:
    def test_owner_access_cannot_be_removed(self, svc, make_resource):
        rid = make_resource("folder", "admin")
        with pytest.raises(PermissionDenied):
            svc.unshare("u1", rid, "owner_u")

    def test_unshare_revokes_access(self, svc, make_resource):
        rid = make_resource("folder", "owner")
        svc.share("u1", rid, "u2", "viewer")
        svc.unshare("u1", rid, "u2")
        assert not svc.can("u2", rid, "view")


@pytest.mark.sharing
class TestDependencyGraph:
    def test_sharing_workflow_grants_view_on_dependency(self, svc):
        kb = svc.create("knowledge_base", "owner_u")
        wf = svc.create("workflow", "owner_u", deps=[kb])
        svc.share("owner_u", wf, "u2", "editor")
        assert svc.can("u2", kb, "view")
        assert not svc.can("u2", kb, "edit")

    def test_unshare_workflow_revokes_dependency_access(self, svc):
        kb = svc.create("knowledge_base", "owner_u")
        wf = svc.create("workflow", "owner_u", deps=[kb])
        svc.share("owner_u", wf, "u2", "editor")
        svc.unshare("owner_u", wf, "u2")
        assert not svc.can("u2", kb, "view")
