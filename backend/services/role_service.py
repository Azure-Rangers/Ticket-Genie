"""
Authorization boundary for knowledge access.

KNOWN GAP: There is currently no real authentication/RBAC system in this
repo (backend/api/auth.py and backend/models/user.py both exist but are
empty placeholders, and the frontend only tracks a mock `role`
("Employee"/"Management") in localStorage with no per-user department).

Because of that, this service cannot yet resolve a verified department for
a given user - it can only work with whatever `role`/`department` the
caller explicitly supplies on the request. It deliberately defaults to the
least-privileged scope set (General only) rather than guessing or granting
broad access, so it never "fakes" security while the real auth/RBAC
integration is still pending.

Once real authentication exists, wire it in by resolving the caller's
verified role/department server-side (e.g. from a session/JWT) instead of
trusting request-supplied values, and pass those into get_allowed_scopes().
"""

from typing import List, Optional

GENERAL_SCOPE = "General"
DEPARTMENT_SCOPES = {"HR", "IT", "Accounting"}
MANAGEMENT_SCOPE = "UpperManagement"


def get_allowed_scopes(
    role: Optional[str], department: Optional[str] = None
) -> List[str]:
    """
    Determine which knowledge scopes a user may see.

    Every user gets General (company-wide, non-restricted) knowledge.
    A department-specific scope is granted only when a matching department
    is explicitly supplied. Management additionally gets the
    UpperManagement scope. Nothing else is granted by default.
    """

    scopes = {GENERAL_SCOPE}

    normalized_department = (department or "").strip()
    if normalized_department in DEPARTMENT_SCOPES:
        scopes.add(normalized_department)

    if (role or "").strip().lower() == "management":
        scopes.add(MANAGEMENT_SCOPE)

    return sorted(scopes)
