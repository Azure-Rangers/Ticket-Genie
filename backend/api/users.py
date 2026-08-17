"""User Profiles API Router for TicketGenie."""

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from database.crud import get_user_profile, update_user_profile
from services.jwt_verifier import verify_azure_user

router = APIRouter(prefix="/users", tags=["users"])


class UserProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None


class AzureLoginRequest(BaseModel):
    azure_object_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    id_token: Optional[str] = None


@router.get("/profile")
def handle_get_profile(
    user_id: Optional[str] = None,
    current_user: dict = Depends(verify_azure_user),
):
    from fastapi import HTTPException
    user_oid = current_user.get("oid")
    user_email = current_user.get("email")
    
    profile = get_user_profile(user_id=user_id, azure_oid=user_oid, email=user_email)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found in database")
    return profile


@router.put("/profile")
def handle_update_profile(
    req: UserProfileUpdateRequest,
    user_id: Optional[str] = None,
    current_user: dict = Depends(verify_azure_user),
):
    target_user_id = user_id or "usr-1"
    return update_user_profile(
        user_id=target_user_id,
        name=req.name,
        email=req.email,
        phone=req.phone,
        department=req.department,
    )


@router.post("/azure-login")
def handle_azure_login(req: AzureLoginRequest):
    from services.jwt_verifier import verify_azure_jwt

    jwt_verified = False
    verified_oid = req.azure_object_id

    if req.id_token:
        try:
            claims = verify_azure_jwt(req.id_token)
            jwt_verified = True
            token_oid = claims.get("oid") or claims.get("sub")
            if token_oid:
                verified_oid = token_oid
            print(f"✅ [Azure Auth API] Microsoft JWT signature verified for OID: {verified_oid}")
        except Exception as err:
            print(f"⚠️ [Azure Auth API] JWT verification warning: {err}")

    from database.connection import SessionLocal
    from database.models_db import DepartmentUserDB

    is_admin = False
    role = "Employee"

    with SessionLocal() as session:
        record = session.query(DepartmentUserDB).filter(
            DepartmentUserDB.azure_object_id == verified_oid
        ).first()
        if record:
            if record.role.lower() in ["admin", "super admin", "operations admin"]:
                is_admin = True
                role = record.role
            # Automatically update user_email on mapping if missing
            if req.email and not record.user_email:
                record.user_email = req.email
                session.commit()

    # Synchronize user_profiles table from JWT claims upon login
    if req.email or req.name:
        try:
            from database.crud import update_user_profile
            profile_id = f"usr-admin-{verified_oid[:8]}"
            update_user_profile(
                user_id=profile_id,
                name=req.name or req.email.split("@")[0],
                email=req.email,
                department=record.department_name if record else "Upper Executive Management",
            )
        except Exception as err:
            print(f"Notice: profile sync during login: {err}")

    print(f"👤 [Azure Auth API] User {verified_oid} authenticated as role: '{role}', is_admin: {is_admin}, jwt_verified: {jwt_verified}")
    return {
        "status": "success",
        "azure_object_id": verified_oid,
        "is_admin": is_admin,
        "role": role,
        "jwt_verified": jwt_verified,
        "email": req.email,
        "name": req.name or "Azure User",
    }

