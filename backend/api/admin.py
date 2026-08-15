"""Super Admin & Governance API Router for TicketGenie."""

from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.crud import (
    add_department_user,
    create_department,
    get_leave_tickets,
    list_department_users,
    list_departments,
    remove_department_user,
)
from services.sql_context_service import execute_sql_query

router = APIRouter(prefix="/admin", tags=["admin"])


class DepartmentCreateRequest(BaseModel):
    name: str
    queue_name: str
    description: Optional[str] = None


class DepartmentUserRequest(BaseModel):
    department_name: str
    azure_object_id: str
    role: Optional[str] = "Member"
    user_email: Optional[str] = None


class SQLQueryRequest(BaseModel):
    query: str
    role: Optional[str] = "Super Admin"
    user_id: Optional[str] = "admin"


@router.get("/departments")
def get_departments():
    return list_departments()


@router.post("/departments", status_code=201)
def handle_create_department(req: DepartmentCreateRequest):
    return create_department(req.name, req.queue_name, req.description)


@router.get("/departments/users")
def get_department_users(department_name: Optional[str] = None):
    return list_department_users(department_name)


@router.post("/departments/users", status_code=201)
def handle_add_department_user(req: DepartmentUserRequest):
    return add_department_user(
        department_name=req.department_name,
        azure_object_id=req.azure_object_id,
        role=req.role or "Member",
        user_email=req.user_email,
    )


@router.delete("/departments/users")
def handle_remove_department_user(department_name: str, azure_object_id: str):
    removed = remove_department_user(department_name, azure_object_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Department user mapping not found")
    return {"message": f"Removed Azure Object ID {azure_object_id} from {department_name}"}


@router.get("/leave-queue")
def get_admin_leave_queue():
    return get_leave_tickets()


@router.post("/sql-query")
def handle_sql_query(req: SQLQueryRequest):
    return execute_sql_query(req.query, role=req.role or "Super Admin", user_id=req.user_id or "admin")
