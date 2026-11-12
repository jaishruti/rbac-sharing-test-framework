"""Tiny in-memory stand-in for a sharing/RBAC platform.

This is the SYSTEM UNDER TEST for the demo. In real use you replace
`Client` in tests/conftest.py with a thin wrapper over your product's
API (or UI driver) -- the tests and matrix stay the same.

Permissions are hard-coded here on purpose: they are the product's
behaviour, while matrix/permissions.yaml is the independent spec.

Set DEMO_BUG=1..3 to inject a regression:
  1 - viewers on knowledge_base can edit (privilege escalation)
  2 - unshare does not revoke access to dependencies
  3 - an editor can share at a role higher than their own
"""
import itertools
import os

RANK = {"none": 0, "viewer": 1, "editor": 2, "admin": 3, "owner": 4}

_BASE = {
    "owner": {"view", "edit", "delete", "share", "unshare"},
    "admin": {"view", "edit", "delete", "share", "unshare"},
    "editor": {"view", "edit"},
    "viewer": {"view"},
    "none": set(),
}

# workflow -> knowledge_base it depends on
DEPENDS_ON = {"workflow": "knowledge_base"}


class PermissionDenied(Exception):
    pass


class Service:
    def __init__(self):
        self.bug = os.getenv("DEMO_BUG", "")
        self._ids = itertools.count(1)
        self.resources = {}   # rid -> {"type", "owner", "deps": [rid]}
        self.acl = {}         # (rid, user) -> role

    # ---- helpers -------------------------------------------------
    def role_of(self, user, rid):
        return self.acl.get((rid, user), "none")

    def _perms(self, rtype, role):
        perms = set(_BASE[role])
        if rtype == "agent" and role == "editor":
            perms.add("share")
        if self.bug == "1" and rtype == "knowledge_base" and role == "viewer":
            perms.add("edit")
        return perms

    def can(self, user, rid, action):
        rtype = self.resources[rid]["type"]
        return action in self._perms(rtype, self.role_of(user, rid))

    # ---- operations ----------------------------------------------
    def create(self, rtype, owner, deps=()):
        rid = f"{rtype}-{next(self._ids)}"
        self.resources[rid] = {"type": rtype, "owner": owner, "deps": list(deps)}
        self.acl[(rid, owner)] = "owner"
        return rid

    def share(self, actor, rid, target, role):
        if not self.can(actor, rid, "share"):
            raise PermissionDenied(f"{actor} cannot share {rid}")
        if role == "owner":
            raise PermissionDenied("ownership cannot be shared")
        if RANK[role] > RANK[self.role_of(actor, rid)] and self.bug != "3":
            raise PermissionDenied("cannot grant a higher role than your own")
        self.acl[(rid, target)] = role
        # sharing a resource grants at least viewer on its dependencies
        for dep in self.resources[rid]["deps"]:
            if RANK[self.role_of(target, dep)] < RANK["viewer"]:
                self.acl[(dep, target)] = "viewer"

    def unshare(self, actor, rid, target):
        if not self.can(actor, rid, "unshare"):
            raise PermissionDenied(f"{actor} cannot unshare {rid}")
        if self.role_of(target, rid) == "owner":
            raise PermissionDenied("owner access cannot be removed")
        self.acl.pop((rid, target), None)
        if self.bug != "2":
            for dep in self.resources[rid]["deps"]:
                if self.role_of(target, dep) == "viewer":
                    self.acl.pop((dep, target), None)
