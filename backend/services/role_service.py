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

from typing import List, NamedTuple, Optional

GENERAL_SCOPE = "General"
DEPARTMENT_SCOPES = {"HR", "IT", "Accounting", "WorkplaceOperations"}
MANAGEMENT_SCOPE = "UpperManagement"

# Roles (from the live department-user assignment vocabulary in
# frontend/management/departments.html's #userRoleSelect) authorized to
# reassign/reprioritize tickets via Genie. Deliberately an exact-match
# allowlist, not a substring check like is_super_admin() below - these are
# fixed, known role strings, not a free-text prefix family. Plain "Member"
# and "Employee" are intentionally excluded.
TICKET_MUTATION_ROLES = {
    "admin",
    "operations admin",
    "department admin",
    "upper executive lead",
    "super admin",
}

# Canonical role vocabulary for the portal employee-assignment flow (Feature
# 3 / create_portal_employee). Deliberately separate from TICKET_MUTATION_ROLES
# above and from models.ticket's department vocabulary - this is the exact
# option set in frontend/management/departments.html's #userRoleSelect, the
# only currently-live UI for assigning a department user. The select also
# offers a free-text "__custom__" role; Genie intentionally does not support
# that path (see final report), only these fixed options.
EMPLOYEE_ASSIGNMENT_ROLES: tuple[str, ...] = (
    "Admin",
    "Super Admin",
    "Operations Admin",
    "Department Admin",
    "Upper Executive Lead",
    "Employee",
    "Member",
)


def is_super_admin(role: Optional[str], is_dev: bool = False) -> bool:
    """The exact rule backend/api/admin.py's require_super_admin enforces.

    Factored out here so every caller that needs the "may manage
    department/role assignments" check (the admin API dependency, and the
    Genie employee-creation flow) shares one definition instead of two
    copies that could drift apart.
    """

    return "super" in (role or "").lower() or is_dev


def is_department_ticketer(role: Optional[str]) -> bool:
    """Whether `role` sees department-ticketer-tier navigation (Inbox,
    Analytics) in the live UI.

    Mirrors frontend/src/lib/stores/auth.js's isTicketer() exactly (a
    substring check against admin/ticketer/manager/super/operations) so
    Genie's navigation gating in services.chatbot_service always agrees
    with what frontend/src/components/Sidebar.svelte actually shows for
    the same role string - not a new, independently-drifting rule.
    """

    normalized = (role or "").lower()
    return any(
        keyword in normalized
        for keyword in ("admin", "ticketer", "manager", "super", "operations")
    )


def is_admin_role(role: Optional[str]) -> bool:
    """Whether `role` sees admin-tier navigation (Settings) in the live UI.

    Mirrors frontend/src/lib/stores/auth.js's isAdmin() exactly (a
    substring check against admin/manager/super/operations).
    """

    normalized = (role or "").lower()
    return any(
        keyword in normalized for keyword in ("admin", "manager", "super", "operations")
    )


def is_ticket_mutation_authorized(role: Optional[str]) -> bool:
    """Whether `role` may reassign a ticket's department or priority.

    Deterministic, backend-only check against TICKET_MUTATION_ROLES. Never
    trust a role from the request body - callers must pass the verified
    role resolved by services.jwt_verifier.verify_azure_user.

    NOTE: this only says whether the role may attempt a mutation at all -
    it says nothing about WHICH tickets. That's a separate question,
    answered by resolve_visibility_scope() below - a role can pass this
    check and still be unable to see/manage a specific ticket.
    """

    return (role or "").strip().lower() in TICKET_MUTATION_ROLES


# Compatibility mapping: portal/RBAC department names (as stored on
# DepartmentUserDB.department_name, assigned via the live
# frontend/management/departments.html UI - the same vocabulary as
# EMPLOYEE_ASSIGNMENT_ROLES above) -> canonical ticket department names
# (models.ticket.TICKET_DEPARTMENTS). ONLY includes pairs that are
# genuinely the same department under both vocabularies, verified against
# the actual current department lists - not inferred from name
# similarity:
#   - "IT Team" / "HR Team" / "Accounting Team" are spelled identically in
#     both vocabularies, so the mapping is exact and safe.
#   - "Upper Executive Management" (assignment vocab) is deliberately NOT
#     mapped to "Upper Management" (ticket vocab) even though the names
#     look related - nothing in the existing codebase (JWT claims,
#     DepartmentUserDB, sql_context_service's role-based SQL scoping)
#     establishes them as the same department. Treating them as
#     equivalent would be an invented mapping, not a verified one.
#   - "Workplace Operations Team" (ticket vocab) has no counterpart in the
#     assignment vocab at all - the live department-assignment UI
#     (#deptSelect) never offers it, so no user can even be assigned
#     there today.
# A department that isn't in this map has no safe ticket-visibility
# scope. Callers MUST fail closed (deny) rather than defaulting to
# unrestricted access - see resolve_visibility_scope().
ASSIGNMENT_TO_TICKET_DEPARTMENT = {
    "IT Team": "IT Team",
    "HR Team": "HR Team",
    "Accounting Team": "Accounting Team",
}


class VisibilityScope(NamedTuple):
    """
    Result of resolve_visibility_scope(): either genuinely unrestricted
    (Super Admin only) or scoped to exactly one canonical ticket
    department. This type deliberately has no "unknown"/"everything"
    state - that case is represented by resolve_visibility_scope()
    returning None, and every caller must treat None as "deny", never as
    "show everything".
    """

    unrestricted: bool
    department: Optional[str]


def resolve_visibility_scope(current_user: Optional[dict]) -> Optional[VisibilityScope]:
    """
    Determine which tickets an authenticated user may see/manage through
    Genie's management actions (reassign_ticket / change_priority).

    Three easily-conflated things this deliberately keeps distinct:
    - "Super Admin" (a current_user role) - the only role with existing,
      explicit org-wide authorization in this codebase (require_super_admin
      already treats any role containing "super" this way for
      portal-employee management; reused here via is_super_admin() for
      ticket visibility too).
    - "Upper Executive Lead" (a TICKET_MUTATION_ROLES role) - authorized to
      ATTEMPT a mutation like Admin/Operations Admin/Department Admin, but
      has no special visibility of its own: its ticket visibility is
      scoped by its assigned department exactly like any other
      non-Super-Admin mutation-authorized role, and fails closed if that
      department doesn't appear in ASSIGNMENT_TO_TICKET_DEPARTMENT.
    - "Upper Management" (a canonical TICKET department, models.ticket) -
      unrelated to either role above; distinct from the "Upper Executive
      Management" ASSIGNMENT department (see ASSIGNMENT_TO_TICKET_DEPARTMENT's
      docstring for why they're not treated as the same thing).

    Returns None when the scope cannot be safely determined. Callers must
    treat None as "deny" - never fall back to showing every ticket.
    """

    role = (current_user or {}).get("role") or ""
    if is_super_admin(role):
        return VisibilityScope(unrestricted=True, department=None)

    assignment_department = (current_user or {}).get("department") or ""
    ticket_department = ASSIGNMENT_TO_TICKET_DEPARTMENT.get(assignment_department)
    if ticket_department:
        return VisibilityScope(unrestricted=False, department=ticket_department)

    return None


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
