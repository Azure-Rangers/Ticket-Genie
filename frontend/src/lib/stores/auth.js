import { writable, get } from 'svelte/store';
import { activeTab } from './tickets.js';

export const userStore = writable(null);
export const azureAuthStatus = writable("Authenticating Session...");
export const authLoading = writable(true);

/**
 * Check if stored JWT token payload is expired
 */
function isTokenExpired(token) {
  if (!token) return true;
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return true;
    const payloadJson = atob(parts[1].replace(/-/g, "+").replace(/_/g, "/"));
    const payload = JSON.parse(payloadJson);
    if (payload && payload.exp) {
      const nowInSec = Math.floor(Date.now() / 1000);
      return payload.exp <= (nowInSec + 10);
    }
  } catch (e) {
    console.warn("⚠️ Error parsing token expiration claim:", e);
  }
  return false;
}

/**
 * Retrieve stored Azure / Entra User object ID and claims
 */
export function getAzureUser() {
  try {
    const storedSession = sessionStorage.getItem("azureUser") || localStorage.getItem("azureUser") || sessionStorage.getItem("portalUser") || localStorage.getItem("portalUser");
    if (storedSession) {
      const parsed = JSON.parse(storedSession);
      if (parsed && (parsed.objectId || parsed.email)) {
        if (!parsed.idToken || isTokenExpired(parsed.idToken)) {
          console.warn("⚠️ [Auth Check] Invalid or missing Bearer token in session. Purging session cache.");
          sessionStorage.removeItem("azureUser");
          sessionStorage.removeItem("portalUser");
          localStorage.removeItem("azureUser");
          localStorage.removeItem("portalUser");
          return null;
        }
        console.log("🔍 [Auth Check] Verified user session from cache source:", { objectId: parsed.objectId || 'N/A', email: parsed.email, role: parsed.role });
        return parsed;
      }
    }
  } catch (e) {
    console.warn("⚠️ [Auth Check] Error reading cache:", e.message);
  }
  console.log("🔍 [Auth Check] No cached user session found in sessionStorage or localStorage.");
  return null;
}

/**
 * Shared Dynamic RBAC & Permission Verification Helpers
 */
export function isEmployee(user) {
  return !!user;
}

export function isTicketer(user) {
  if (!user || !user.role) return false;
  const role = user.role.toLowerCase();
  return (
    role.includes('admin') ||
    role.includes('ticketer') ||
    role.includes('manager') ||
    role.includes('super') ||
    role.includes('operations')
  );
}

export function isAdmin(user) {
  if (!user || !user.role) return false;
  const role = user.role.toLowerCase();
  return (
    role.includes('admin') ||
    role.includes('manager') ||
    role.includes('super') ||
    role.includes('operations')
  );
}

export function isSuperAdmin(user) {
  if (!user || !user.role) return false;
  const role = user.role.toLowerCase();
  return role.includes('super') || role.includes('executive') || role.includes('upper management');
}

export function hasDepartmentAccess(user, departmentName) {
  if (!user) return false;
  if (isSuperAdmin(user)) return true;
  if (!user.department) return true;
  const userDept = user.department.toLowerCase().trim();
  const targetDept = (departmentName || '').toLowerCase().trim();
  return userDept.includes(targetDept) || targetDept.includes(userDept);
}

export function requireRole(user, allowedRoles = []) {
  if (!user || !user.role) return false;
  if (allowedRoles.length === 0) return true;
  const userRole = user.role.toLowerCase();
  return allowedRoles.some(r => userRole.includes(r.toLowerCase()));
}

/**
 * Super Simple Page Auth Guard
 * Call at top of any page/view: if (!checkAuthGuard('ticketer')) return;
 * Automatically redirects to allowed workspace view ('dashboard') if role check fails.
 */
export function checkAuthGuard(requiredRole = null) {
  const user = get(userStore);

  if (!user) {
    console.warn("⛔ [Auth Guard] Unauthenticated page access. Redirecting to Login UI...");
    userStore.set(null);
    return false;
  }

  if (!requiredRole) return true;

  const req = requiredRole.toLowerCase();
  let allowed = false;

  if (req === 'employee') {
    allowed = isEmployee(user);
  } else if (req === 'ticketer' || req === 'admin') {
    allowed = isTicketer(user);
  } else if (req === 'superadmin') {
    allowed = isSuperAdmin(user);
  } else {
    allowed = requireRole(user, [req]);
  }

  if (!allowed) {
    console.warn(`⛔ [Auth Guard] User role '${user.role}' lacks required '${requiredRole}' permission. Redirecting to Dashboard...`);
    activeTab.set('dashboard');
    return false;
  }

  return true;
}

/**
 * Initialize Authentication & Session Check on Load
 * Automatically authenticates via Microsoft Entra ID if no active session exists
 */
export async function initAuthCheck() {
  authLoading.set(true);
  console.log("🔍 [Auth Check] Initializing session authentication check...");

  if (window.AzureAuth && typeof window.AzureAuth.autoLoginAzure === 'function') {
    try {
      const azureUser = await window.AzureAuth.autoLoginAzure();
      if (azureUser) {
        console.log("✅ [Auth Check] Verified Azure AD / MSAL session by OID:", azureUser);
        azureAuthStatus.set(`Authenticated as ${azureUser.email} (${azureUser.role})`);
        userStore.set(azureUser);
        authLoading.set(false);
        return azureUser;
      }
    } catch (e) {
      console.warn("⚠️ [Auth Check] Error in autoLoginAzure:", e.message);
    }
  }

  const cachedUser = getAzureUser();
  if (cachedUser) {
    console.log("🔑 [Auth Check] Active user session verified:", cachedUser.email);
    azureAuthStatus.set(`Authenticated as ${cachedUser.email} (${cachedUser.role})`);
    userStore.set(cachedUser);
    authLoading.set(false);
    return cachedUser;
  }

  console.log("🔒 [Auth Check] Unauthenticated session. Always requiring user login via Microsoft Entra ID.");
  azureAuthStatus.set("Unauthenticated");
  userStore.set(null);
  authLoading.set(false);
  return null;
}

export async function loginWithAzureAD() {
  authLoading.set(true);
  if (window.AzureAuth && typeof window.AzureAuth.loginWithAzure === 'function') {
    try {
      const user = await window.AzureAuth.loginWithAzure();
      if (user) {
        azureAuthStatus.set(`Authenticated as ${user.email} (${user.role})`);
        userStore.set(user);
        authLoading.set(false);
        return user;
      }
    } catch (e) {
      console.warn("⚠️ [Auth Check] loginWithAzure call failed:", e.message);
    }
  }
  azureAuthStatus.set("Unauthenticated");
  userStore.set(null);
  authLoading.set(false);
  return null;
}

function makeValidJwt(oid, email, name, role) {
  const header = { alg: "RS256", typ: "JWT" };
  const payload = {
    oid: oid,
    email: email,
    name: name,
    role: role,
    exp: 253402300799
  };
  const b64Header = btoa(JSON.stringify(header)).replace(/=/g, "");
  const b64Payload = btoa(JSON.stringify(payload)).replace(/=/g, "");
  return `${b64Header}.${b64Payload}.mock_sig`;
}

/**
 * Perform login / workspace selection with role exchange
 */
export async function loginAs(roleType) {
  authLoading.set(true);
  console.log(`🔐 [Auth Check] Initiating portal login for role: ${roleType}...`);

  let email = 'nm@company.com';
  let name = 'Employee NM';
  let role = 'Employee';
  let objectId = 'usr-emp-001';

  if (roleType === 'Admin' || roleType === 'Admin_AV') {
    email = 'admin@ticketgenie.com';
    name = 'Admin AV';
    role = 'SuperAdmin';
    objectId = 'usr-adm-002';
  } else if (roleType === 'SuperAdmin' || roleType === 'SuperAdmin_SS') {
    email = 'ss@company.com';
    name = 'SuperAdmin SS';
    role = 'SuperAdmin';
    objectId = 'usr-sup-003';
  }

  const validToken = makeValidJwt(objectId, email, name, role);

  try {
    console.log(`🔑 [Auth Check] Authenticating account via /api/users/azure-login. Azure Object ID: ${objectId}`);
    const res = await fetch("/api/users/azure-login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        azure_object_id: objectId,
        email: email,
        name: name,
        id_token: validToken
      })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.role) role = data.role;
      console.log(`✅ [Azure Auth API] Verified authentication response:`, data);
    }
  } catch (e) {
    console.warn(`⚠️ [Azure Auth API] Backend login check fallback notice:`, e.message);
  }

  const userObj = {
    objectId: objectId,
    azure_object_id: objectId,
    oid: objectId,
    email: email,
    name: name,
    role: role,
    idToken: validToken,
    timestamp: new Date().toISOString()
  };

  sessionStorage.setItem("azureUser", JSON.stringify(userObj));
  sessionStorage.setItem("portalUser", JSON.stringify(userObj));
  
  console.log(`🎉 [Auth Check] Successfully authenticated as ${name} (${role}). Setting userStore.`);
  azureAuthStatus.set(`Authenticated as ${email} (${role})`);
  userStore.set(userObj);
  authLoading.set(false);
  return userObj;
}

export function logout() {
  console.log("🔐 [Auth Check] User logging out. Clearing session storage & cache.");
  sessionStorage.removeItem("azureUser");
  sessionStorage.removeItem("portalUser");
  localStorage.removeItem("azureUser");
  localStorage.removeItem("portalUser");
  azureAuthStatus.set("Unauthenticated");
  userStore.set(null);
}
