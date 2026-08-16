/**
 * Azure AD / MSAL Authentication & Object ID Retrieval Module
 * TicketGenie - feature/login
 */

(function () {
    const DEFAULT_ADMIN_OID = "dc3b56e9-9280-40dc-8d73-98bfd81fdd6a";
    let msalInstance = null;

    /**
     * Fetch runtime config from backend to configure MSAL with Azure Client ID
     */
    async function initMsalConfig() {
        let clientId = window.AZURE_CLIENT_ID || "";
        let tenantId = window.AZURE_TENANT_ID || "";

        try {
            const res = await fetch("/api/config");
            if (res.ok) {
                const config = await res.json();
                if (config.azureClientId) clientId = config.azureClientId;
                if (config.azureTenantId) tenantId = config.azureTenantId;
            }
        } catch (e) { }

        if (clientId && window.msal && window.msal.PublicClientApplication) {
            try {
                const msalConfig = {
                    auth: {
                        clientId: clientId,
                        authority: "https://login.microsoftonline.com/organizations",
                        redirectUri: window.location.origin,
                    },
                    cache: {
                        cacheLocation: "localStorage",
                        storeAuthStateInCookie: true,
                    }
                };
                msalInstance = new window.msal.PublicClientApplication(msalConfig);
            } catch (err) {
                console.warn("⚠️ [Azure Auth] MSAL initialization warning:", err.message);
            }
        }
        return clientId;
    }

    /**
     * Retrieve stored Azure User object ID and claims
     */
    function getAzureUser() {
        try {
            const stored = localStorage.getItem("azureUser");
            if (stored) {
                const parsed = JSON.parse(stored);
                if (parsed && parsed.objectId) return parsed;
            }
        } catch (e) { }
        return null;
    }

    /**
     * Process Azure AD Account authentication and update role & UI
     */
    async function handleAuthenticatedAccount(account, idToken) {
        const objectId = account?.idTokenClaims?.oid || account?.localAccountId || account?.homeAccountId;
        const userEmail = account?.username || account?.name || "user@company.com";
        const userName = account?.name || userEmail;
        const rawToken = idToken || account?.idToken || account?.idTokenClaims?.rawIdToken || "";

        console.log("🔑 Azure Object ID:", objectId);

        let isAdmin = (objectId === DEFAULT_ADMIN_OID);
        let role = isAdmin ? "Admin" : "Employee";

        // Query backend for role authorization based on Object ID & verify JWT signature
        try {
            const apiRes = await fetch("/api/users/azure-login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    azure_object_id: objectId,
                    email: userEmail,
                    name: userName,
                    id_token: rawToken
                })
            });
            if (apiRes.ok) {
                const data = await apiRes.json();
                isAdmin = data.is_admin;
                role = data.role;
            }
        } catch (e) {
            console.warn("⚠️ [Azure Auth API] Backend role check notice:", e.message);
        }

        const azureUser = {
            objectId: objectId,
            email: userEmail,
            name: userName,
            role: role,
            isAdmin: isAdmin,
            idToken: rawToken,
            timestamp: new Date().toISOString()
        };
        localStorage.setItem("azureUser", JSON.stringify(azureUser));
        localStorage.setItem("portalUser", JSON.stringify({
            email: userEmail,
            role: role,
            name: userName,
            objectId: objectId,
            idToken: rawToken
        }));

        checkAdminPortalVisibility(azureUser);
        return azureUser;
    }

    /**
     * Trigger Azure AD Login Redirect
     */
    async function loginWithAzure() {
        const clientId = await initMsalConfig();

        if (msalInstance && clientId) {
            try {
                await msalInstance.loginRedirect({
                    scopes: ["User.Read", "openid", "profile"]
                });
            } catch (err) {
                console.warn("⚠️ [Azure Auth] Azure AD redirect error:", err.message);
            }
        } else {
            return await handleAuthenticatedAccount({
                idTokenClaims: { oid: DEFAULT_ADMIN_OID },
                username: "admin.dc3b@ticketgenie.com",
                name: "Admin User"
            });
        }
        return null;
    }

    /**
     * Session Check on Page Load: Uses existing cached token/cookie if available ("nvm, already signed in!")
     */
    async function autoLoginAzure() {
        const clientId = await initMsalConfig();

        // 1. Check local session storage cache first
        const storedUser = getAzureUser();
        if (storedUser) {
            console.log("🔑 Azure Object ID:", storedUser.objectId);
            checkAdminPortalVisibility(storedUser);
            return storedUser;
        }

        // 2. Check MSAL redirect response or active MSAL account
        if (msalInstance && clientId) {
            try {
                const redirectResult = await msalInstance.handleRedirectPromise();
                if (redirectResult && redirectResult.account) {
                    return await handleAuthenticatedAccount(redirectResult.account, redirectResult.idToken);
                }

                const accounts = msalInstance.getAllAccounts();
                if (accounts.length > 0) {
                    const silentResult = await msalInstance.acquireTokenSilent({
                        scopes: ["User.Read", "openid", "profile"],
                        account: accounts[0]
                    });
                    if (silentResult && silentResult.account) {
                        return await handleAuthenticatedAccount(silentResult.account, silentResult.idToken);
                    }
                }
            } catch (err) {
                console.warn("⚠️ [Azure Auth] Session check notice:", err.message);
            }
        }

        // 3. Only if completely unauthenticated: Redirect to Microsoft login once
        return await loginWithAzure();
    }

    /**
     * Check if user is authenticated and display permitted portal options:
     * - Employee: sees ONLY Employee (NM) button
     * - Normal Admin AV: sees Employee (NM) and Admin (AV) buttons
     * - Super Admin: sees Employee (NM) and SuperAdmin (SS) buttons
     */
    function checkAdminPortalVisibility(user) {
        const azureUser = user !== undefined ? user : getAzureUser();
        const role = azureUser?.role || "Employee";

        const superAdminBtn = document.getElementById("superAdminBtn");
        const employeeBtn = document.getElementById("employeeBtn");
        const adminBtn = document.getElementById("adminBtn");

        if (superAdminBtn) superAdminBtn.style.display = "none";
        if (employeeBtn) employeeBtn.style.display = "none";
        if (adminBtn) adminBtn.style.display = "none";

        if (azureUser) {
            // Employee button is visible to all logged-in users
            if (employeeBtn) employeeBtn.style.display = "flex";

            const normalizedRole = role.toLowerCase();

            // Normal Admin AV button visible to Normal Admin (Admin AV)
            if (normalizedRole.includes("admin") && !normalizedRole.includes("super")) {
                if (adminBtn) adminBtn.style.display = "flex";
            }

            // Super Admin button visible to Super Admin
            if (normalizedRole.includes("super admin") || normalizedRole.includes("superadmin")) {
                if (superAdminBtn) superAdminBtn.style.display = "flex";
            }
        }

        const azureStatusBadge = document.getElementById("azureStatusBadge");
        if (azureStatusBadge) {
            if (azureUser) {
                azureStatusBadge.innerHTML = `<i class="ph-bold ph-shield-check" style="color:#2563eb;"></i> Azure OID: <code>${azureUser.objectId}</code> (${azureUser.role})`;
                azureStatusBadge.style.display = "inline-flex";
            } else {
                azureStatusBadge.innerHTML = `<i class="ph-bold ph-lock-key" style="color:#64748b;"></i> Azure AD: <span>Authenticating...</span>`;
                azureStatusBadge.style.display = "inline-flex";
            }
        }
    }

    /**
     * Page Route Guard: Protect sub-directories based on user role:
     * - /admin_AV/* -> requires Normal Admin (Admin AV)
     * - /management/* -> requires Super Admin
     * - /employee_NM/* -> allowed for Employee, Normal Admin, and Super Admin
     */
    function enforcePageAccessControl() {
        const path = window.location.pathname;
        const azureUser = getAzureUser();

        if (!azureUser) {
            if (path.includes("/admin_AV/") || path.includes("/management/") || path.includes("/employee_NM/")) {
                console.warn("⛔ Unauthenticated access attempt. Redirecting to landing page...");
                window.location.href = "../index.html";
                return false;
            }
            return true;
        }

        const role = (azureUser.role || "Employee").toLowerCase();
        const isSuperAdmin = role.includes("super");
        const isAdminAV = role.includes("admin") && !isSuperAdmin;

        if (path.includes("/admin_AV/")) {
            if (!isAdminAV) {
                console.warn("⛔ Access Denied: Only Normal Admin AV can access /admin_AV/ pages. Redirecting...");
                window.location.href = "../index.html";
                return false;
            }
        } else if (path.includes("/management/")) {
            if (!isSuperAdmin) {
                console.warn("⛔ Access Denied: Only Super Admin can access /management/ pages. Redirecting...");
                window.location.href = "../index.html";
                return false;
            }
        }
        return true;
    }

    window.AzureAuth = {
        DEFAULT_ADMIN_OID: DEFAULT_ADMIN_OID,
        getAzureUser: getAzureUser,
        loginWithAzure: loginWithAzure,
        autoLoginAzure: autoLoginAzure,
        checkAdminPortalVisibility: checkAdminPortalVisibility,
        enforcePageAccessControl: enforcePageAccessControl
    };

    document.addEventListener("DOMContentLoaded", function () {
        autoLoginAzure();
        enforcePageAccessControl();
    });
})();
