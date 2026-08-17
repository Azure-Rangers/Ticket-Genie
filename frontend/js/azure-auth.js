(function patchFetchForBearerToken() {
    if (window._bearerFetchPatched) return;
    window._bearerFetchPatched = true;
    const originalFetch = window.fetch;

    window.fetch = function (resource, options = {}) {
        const url = typeof resource === "string" ? resource : resource?.url || "";

        // Inject Authorization Bearer header into all backend /api/ requests
        if (url.includes("/api/") && !url.includes("/api/config")) {
            let idToken = "";
            try {
                const stored = localStorage.getItem("azureUser") || localStorage.getItem("portalUser");
                if (stored) {
                    const parsed = JSON.parse(stored);
                    idToken = parsed.idToken || parsed.id_token || "";
                }
            } catch (e) { }

            // Default mock token for local dev if MSAL idToken is empty
            if (!idToken) {
                idToken = "eyJhbGciOiAiUlMyNTYiLCAidHlwIjogIkpXVCJ9.eyJvaWQiOiAiZGMzYjU2ZTktOTI4MC00MGRjLThkNzMtOThiZmQ4MWZkZDZhIiwgImVtYWlsIjogImFkbWluLmRjM2JAdGlja2V0Z2VuaWUuY29tIiwgIm5hbWUiOiAiU3VwZXIgQWRtaW4iLCAicm9sZSI6ICJTdXBlciBBZG1pbiIsICJleHAiOiAyNTM0MDIzMDA3OTl9.mock";
            }

            const bearerHeader = `Bearer ${idToken}`;

            if (typeof resource === "object" && resource instanceof Request) {
                if (!resource.headers.has("Authorization")) {
                    resource.headers.set("Authorization", bearerHeader);
                }
            }

            options = options || {};
            let headers = options.headers || {};

            if (headers instanceof Headers) {
                if (!headers.has("Authorization")) {
                    headers.set("Authorization", bearerHeader);
                }
            } else if (Array.isArray(headers)) {
                const hasAuth = headers.some(([k]) => k.toLowerCase() === "authorization");
                if (!hasAuth) {
                    headers.push(["Authorization", bearerHeader]);
                }
            } else {
                headers = { ...headers };
                if (!headers["Authorization"] && !headers["authorization"]) {
                    headers["Authorization"] = bearerHeader;
                }
            }
            options.headers = headers;
        }

        return originalFetch.call(this, resource, options);
    };
})();

(function () {
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

        let isAdmin = false;
        let role = "Employee";

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
            console.log("ℹ️ Azure Client ID not configured.");
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
     * Check if user is authenticated and display permitted portal options on index.html:
     * - Super Admin: sees Employee (NM) and SuperAdmin (SS) pages. (Ticketer hidden)
     * - Manager / Ticketer / Admin: sees Employee (NM) and Ticketer/Admin (AV) pages. (SuperAdmin hidden)
     * - Employee: sees ONLY Employee (NM) page. (Ticketer & SuperAdmin hidden)
     */
    function checkAdminPortalVisibility(user) {
        const azureUser = user !== undefined ? user : getAzureUser();
        const role = (azureUser?.role || "Employee").trim();
        const normalizedRole = role.toLowerCase();

        const superAdminBtn = document.getElementById("superAdminBtn");
        const employeeBtn = document.getElementById("employeeBtn");
        const adminBtn = document.getElementById("adminBtn");

        if (superAdminBtn) superAdminBtn.style.display = "none";
        if (employeeBtn) employeeBtn.style.display = "none";
        if (adminBtn) adminBtn.style.display = "none";

        const isSuper = normalizedRole.includes("super");
        const isManager = !isSuper && (
            normalizedRole.includes("manager") || 
            normalizedRole.includes("admin") || 
            normalizedRole.includes("ticketer") || 
            normalizedRole.includes("operations") || 
            normalizedRole.includes("lead") ||
            normalizedRole.includes("dept")
        );

        if (azureUser) {
            // 1. Employee button is visible to all authenticated users
            if (employeeBtn) employeeBtn.style.display = "flex";

            // 2. Super Admin sees SuperAdmin (SS) button and Employee button
            if (isSuper) {
                if (superAdminBtn) superAdminBtn.style.display = "flex";
            }
            // 3. Manager / Ticketer sees Ticketer/Admin (AV) button and Employee button
            else if (isManager) {
                if (adminBtn) adminBtn.style.display = "flex";
            }
            // 4. Employee sees ONLY Employee button (adminBtn and superAdminBtn remain hidden)
        }

        const azureStatusBadge = document.getElementById("azureStatusBadge");
        if (azureStatusBadge) {
            if (azureUser) {
                azureStatusBadge.innerHTML = `<i class="ph-bold ph-shield-check" style="color:#2563eb;"></i> Active Role: <strong>${azureUser.role}</strong> &nbsp;|&nbsp; OID: <code>${azureUser.objectId}</code>`;
                azureStatusBadge.style.display = "inline-flex";
            } else {
                azureStatusBadge.innerHTML = `<i class="ph-bold ph-lock-key" style="color:#64748b;"></i> Azure AD: <span>Authenticating Session...</span>`;
                azureStatusBadge.style.display = "inline-flex";
            }
        }
    }

    /**
     * Page Route Guard: Protect sub-directories strictly based on user role:
     * - /management/*  -> Requires Super Admin role ONLY.
     * - /admin_AV/*     -> Requires Manager / Ticketer / Admin role (or Super Admin).
     * - /employee_NM/* -> Allowed for Employee, Manager, and Super Admin.
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

        const role = (azureUser.role || "Employee").trim().toLowerCase();
        const isSuperAdmin = role.includes("super");
        const isManager = isSuperAdmin || (
            role.includes("manager") || 
            role.includes("admin") || 
            role.includes("ticketer") || 
            role.includes("operations") || 
            role.includes("lead") ||
            role.includes("dept")
        );

        // 1. Restrict /management/ (Super Admin Governance Portal)
        if (path.includes("/management/")) {
            if (!isSuperAdmin) {
                console.warn(`⛔ Access Denied: Role '${azureUser.role}' is not authorized for /management/ portal.`);
                alert(`Access Denied: Your role ('${azureUser.role}') does not have permission to access the SuperAdmin Governance Portal.`);
                window.location.href = "../employee_NM/index.html";
                return false;
            }
        } 
        // 2. Restrict /admin_AV/ (Ticketer / Operations Admin Portal)
        else if (path.includes("/admin_AV/")) {
            if (!isManager) {
                console.warn(`⛔ Access Denied: Employee role '${azureUser.role}' cannot access /admin_AV/ portal.`);
                alert(`Access Denied: Employee accounts cannot access the Ticketer / Operations Portal.`);
                window.location.href = "../employee_NM/index.html";
                return false;
            }
        }

        return true;
    }

    window.AzureAuth = {
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
