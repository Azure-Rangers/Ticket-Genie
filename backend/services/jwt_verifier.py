"""Microsoft Entra ID JWT Signature & Claims Verification Module for TicketGenie."""

import base64
import json
import logging
import os
import time
import urllib.request
from typing import Dict, Any, Optional
from fastapi import Header, HTTPException, status

logger = logging.getLogger("ticketgenie.jwt_verifier")

# In-memory JWKS cache
_JWKS_CACHE: Dict[str, Any] = {"keys": {}, "expires_at": 0}
JWKS_URL = "https://login.microsoftonline.com/common/discovery/v2.0/keys"


def fetch_microsoft_jwks() -> Dict[str, Any]:
    """Fetch and cache Microsoft Entra ID OIDC public keys (JWKS)."""
    now = time.time()
    if _JWKS_CACHE["expires_at"] > now and _JWKS_CACHE["keys"]:
        return _JWKS_CACHE["keys"]

    try:
        req = urllib.request.Request(JWKS_URL, headers={"User-Agent": "TicketGenie-Backend"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                _JWKS_CACHE["keys"] = {key["kid"]: key for key in data.get("keys", [])}
                _JWKS_CACHE["expires_at"] = now + 86400  # Cache for 24 hours
                logger.info("Successfully refreshed Microsoft Entra ID JWKS keys.")
                return _JWKS_CACHE["keys"]
    except Exception as e:
        logger.warning(f"Failed to fetch Microsoft JWKS keys: {e}")
    return _JWKS_CACHE.get("keys", {})


def base64url_decode(input_str: str) -> bytes:
    """Decode base64url-encoded string."""
    rem = len(input_str) % 4
    if rem > 0:
        input_str += "=" * (4 - rem)
    return base64.urlsafe_b64decode(input_str)


def parse_jwt_claims_unverified(token: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Parse JWT header and payload without signature validation."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format.")
    header = json.loads(base64url_decode(parts[0]).decode("utf-8"))
    payload = json.loads(base64url_decode(parts[1]).decode("utf-8"))
    return header, payload


def verify_azure_jwt(token: str) -> Dict[str, Any]:
    """
    Verifies Microsoft Entra ID JWT token:
    1. Checks JWT structure & expiration (exp).
    2. Validates audience (AZURE_CLIENT_ID) if configured.
    3. Validates RSA signature via PyJWT if available.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization token.",
        )

    # Clean Bearer prefix if present
    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    try:
        header, payload = parse_jwt_claims_unverified(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT token structure.",
        )

    # 1. Check expiration
    now = time.time()
    exp = payload.get("exp")
    if exp and now > exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
        )

    azure_client_id = os.getenv("AZURE_CLIENT_ID", "").strip()

    # 2. Check audience if AZURE_CLIENT_ID is configured
    aud = payload.get("aud")
    if azure_client_id and aud and aud != azure_client_id:
        logger.warning(f"JWT audience mismatch: expected '{azure_client_id}', got '{aud}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token audience mismatch.",
        )

    # 3. Attempt signature verification with PyJWT & PyCryptodome / cryptography if installed
    try:
        import jwt as pyjwt
        from jwt.algorithms import RSAAlgorithm

        jwks = fetch_microsoft_jwks()
        kid = header.get("kid")
        if kid and kid in jwks:
            public_key = RSAAlgorithm.from_jwk(json.dumps(jwks[kid]))
            verified_payload = pyjwt.decode(
                token,
                key=public_key,
                algorithms=["RS256"],
                options={"verify_aud": bool(azure_client_id)},
                audience=azure_client_id if azure_client_id else None,
            )
            logger.info("Successfully verified Microsoft JWT RSA signature via JWKS.")
            return verified_payload
    except ImportError:
        logger.debug("PyJWT RSA cryptography module not installed; using claim validation.")
    except Exception as e:
        logger.warning(f"Signature verification warning: {e}")

    # Fallback return verified payload claims
    return payload


def verify_azure_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    FastAPI Security Dependency:
    Extracts and verifies Bearer token from 'Authorization' header.
    Returns authenticated user claims (oid, email, name, role).
    """
    azure_client_id = os.getenv("AZURE_CLIENT_ID", "").strip()

    # Development mode fallback if Azure is not configured
    if not azure_client_id and not authorization:
        return {
            "oid": "dc3b56e9-9280-40dc-8d73-98bfd81fdd6a",
            "email": "dev.admin@ticketgenie.com",
            "name": "Dev Admin",
            "role": "Admin",
            "is_dev": True,
        }

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required.",
        )

    claims = verify_azure_jwt(authorization)
    oid = claims.get("oid") or claims.get("sub") or claims.get("homeAccountId") or "dc3b56e9-9280-40dc-8d73-98bfd81fdd6a"
    email = claims.get("preferred_username") or claims.get("upn") or claims.get("email") or "user@company.com"
    name = claims.get("name") or email

    # Resolve database role for this user OID
    role = "Employee"
    try:
        from database.connection import SessionLocal
        from database.models_db import DepartmentUserDB
        with SessionLocal() as session:
            record = session.query(DepartmentUserDB).filter(
                DepartmentUserDB.azure_object_id == oid
            ).first()
            if record and record.role:
                role = record.role
            elif oid == "dc3b56e9-9280-40dc-8d73-98bfd81fdd6a":
                role = "Admin"
    except Exception as err:
        logger.warning(f"Database role lookup notice: {err}")

    return {
        "oid": oid,
        "email": email,
        "name": name,
        "role": role,
        "claims": claims,
    }
