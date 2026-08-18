"""Super Admin & Governance API Router for TicketGenie."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from database.crud import (
    add_department_user,
    create_department,
    get_leave_tickets,
    list_department_users,
    list_departments,
    remove_department_user,
)
from services.jwt_verifier import verify_azure_user
from services.role_service import is_super_admin
from services.sql_context_service import execute_sql_query

router = APIRouter(prefix="/admin", tags=["admin"])


def require_super_admin(current_user: dict = Depends(verify_azure_user)):
    """Enforce that only SuperAdmin can create/modify roles and department assignments."""
    if not is_super_admin(current_user.get("role"), current_user.get("is_dev", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Only Super Admin can manage department role assignments.",
        )
    return current_user


class DepartmentCreateRequest(BaseModel):
    name: str
    queue_name: str
    description: Optional[str] = None


class DepartmentUserRequest(BaseModel):
    department_name: Optional[str] = None
    department: Optional[str] = None
    azure_object_id: Optional[str] = None
    object_id: Optional[str] = None
    role: Optional[str] = "Member"
    name: Optional[str] = None
    email: Optional[str] = None
    user_email: Optional[str] = None


class SQLQueryRequest(BaseModel):
    query: str
    role: Optional[str] = None
    user_id: Optional[str] = None


@router.get("/departments")
def get_departments(current_user: dict = Depends(verify_azure_user)):
    return list_departments()


@router.post("/departments", status_code=201)
def handle_create_department(
    req: DepartmentCreateRequest,
    current_user: dict = Depends(verify_azure_user),
):
    require_super_admin(current_user)
    return create_department(req.name, req.queue_name, req.description)


@router.get("/departments/users")
def get_department_users(
    department_name: Optional[str] = None,
    current_user: dict = Depends(verify_azure_user),
):
    return list_department_users(department_name)


@router.post("/departments/users", status_code=201)
def assign_department_user(
    req: DepartmentUserRequest,
    current_user: dict = Depends(require_super_admin),
):
    oid = req.azure_object_id or req.object_id
    dept = req.department_name or req.department or "IT Engineering"
    user_email = req.user_email or req.email

    if not oid:
        raise HTTPException(
            status_code=400,
            detail="azure_object_id or object_id is required.",
        )

    return add_department_user(
        department_name=dept,
        azure_object_id=oid,
        role=req.role or "Member",
        user_email=user_email,
    )


@router.delete("/departments/users")
def handle_remove_department_user(
    department_name: str,
    azure_object_id: str,
    current_user: dict = Depends(verify_azure_user),
):
    require_super_admin(current_user)
    removed = remove_department_user(department_name, azure_object_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Department user mapping not found")
    return {
        "message": f"Removed Azure Object ID {azure_object_id} from {department_name}"
    }


@router.get("/leave-queue")
def get_admin_leave_queue(current_user: dict = Depends(verify_azure_user)):
    return get_leave_tickets()


@router.post("/sql-query")
def handle_sql_query(
    req: SQLQueryRequest,
    current_user: dict = Depends(verify_azure_user),
):
    absorbed_role = current_user.get("role") or req.role or "Employee"
    absorbed_user_id = (
        current_user.get("oid") or current_user.get("email") or req.user_id or "admin"
    )

    return execute_sql_query(req.query, role=absorbed_role, user_id=absorbed_user_id)
