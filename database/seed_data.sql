-- ==========================================================
-- TicketGenie Initial Seed Data (SQL)
-- ==========================================================

-- Seed Initial Admin in Department Users
INSERT OR IGNORE INTO department_users (id, department_name, azure_object_id, role, user_email, createdAt)
VALUES (
    'uobj-admin-dc3b56e9',
    'IT',
    'dc3b56e9-9280-40dc-8d73-98bfd81fdd6a',
    'Super Admin',
    'admin.dc3b@ticketgenie.com',
    '2026-08-16T12:00:00'
);

-- Seed Initial Admin in User Profiles
INSERT OR IGNORE INTO user_profiles (id, name, email, role, department, phone, avatar)
VALUES (
    'usr-admin-dc3b56e9',
    'Admin User',
    'admin.dc3b@ticketgenie.com',
    'Super Admin',
    'IT',
    '+1 (555) 019-9999',
    'AV'
);
